import os
import weakref
import copy
from typing import Any

from datasette import hookimpl
from datasette.app import Datasette
from datasette.database import Database
from datasette.plugins import pm

from kaithem.api import web as webapi
from kaithem.api.modules import filename_for_file_resource
from kaithem.api.web import dialogs
from kaithem.src.modules_state import ResourceType, resource_types
from kaithem.src.resource_types import ResourceDictType, mutable_copy_resource
from starlette.responses import Response

import datasette_write  # noqa
import datasette_write_ui  # noqa
import datasette_edit_schema  # noqa
import datasette_comments  # noqa

# Broken https://github.com/datasette/datasette-column-sum/issues/2
# import datasette_column_sum  # noqa
import datasette_checkbox  # noqa


# Config listed by database name
db_cfg_by_module_resource = {}
db_cfg_by_datasette_id = {}


class ConfiguredDB:
    def __init__(self, module: str, resource: str, data: ResourceDictType):
        self.db: Database | None = None
        self.id = (module, resource)
        self.read_perms = data["read_perms"]
        self.write_perms = data["write_perms"]
        self.file = data["database_file"]
        self.name = data["database_name"]


datasette_instance = Datasette(
    [],
    settings={
        "base_url": "/datasette/",
    },
    metadata={
        "plugins": {
            "datasette-cluster-map": {
                "tile_layer": "/maptiles/tile/{z}/{x}/{y}.png",
                "tile_layer_options": {
                    "attribution": '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
                    "maxZoom": 17,
                },
            }
        },
    },
)


datasette_application = datasette_instance.app()


# Workaround for https://github.com/simonw/datasette/issues/2347
# And quick hack to add a static path
class AsgiFilter:
    async def __call__(self, scope, receive, send):
        if scope["path"].startswith("/datasette/datasette/"):
            scope = copy.deepcopy(scope)
            scope["path"] = scope["path"].replace(
                "/datasette/datasette/", "/datasette/", 1
            )
            scope["raw_path"] = scope["raw_path"].replace(
                b"/datasette/datasette/", b"/datasette/", 1
            )
        return await datasette_application(scope, receive, send)


webapi.add_asgi_app("/datasette", AsgiFilter())


class pluggyhooks:
    @hookimpl
    def actor_from_request(self, datasette, request):
        try:
            return {"id": webapi.user(request.scope)}
        except Exception:
            return None

    @hookimpl
    def permission_allowed(self, datasette, actor, action, resource):
        if isinstance(resource, tuple):
            resource = resource[0]
        if actor is None:
            return None

        if resource:
            if not isinstance(resource, str):
                resource = resource.name
            cfg = db_cfg_by_datasette_id[resource]
        else:
            if action == "view-instance":
                return webapi.has_permission("enumerate_endpoints", user=actor["id"])

            return webapi.has_permission("system.admin", user=actor["id"])

        read = {
            "view-database",
            "view-instance",
            "view-table",
            "view-query",
        }
        write = {
            "insert-row",
            "delete-row",
            "update-row",
        }

        if action in read:
            return webapi.has_permission(cfg.read_perms, user=actor["id"])

        if action in write:
            return webapi.has_permission(cfg.write_perms, user=actor["id"])
        else:
            return webapi.has_permission("system.admin", user=actor["id"])

pm.register(pluggyhooks())


class DatasetteResourceType(ResourceType):
    def blurb(self, module, resource, data):
        return f"""
        <div class="tool-bar">
            <a href="/datasette/{data['database_name']}">
            <span class="mdi mdi-database"></span>
            Datasette</a>
        </div>
        """

    def check_conflict(self, module: str, resource: str, data: ResourceDictType):
        for i in db_cfg_by_module_resource:
            if i == (module, resource):
                continue
            if db_cfg_by_module_resource[i].name == data["database_name"]:
                raise Exception(f"Database already open: {data['database_name']}")
            if db_cfg_by_module_resource[i].file == data["database_file"]:
                raise Exception(f"Database already open: {data['database_file']}")

    def on_load(self, module: str, resource: str, data: ResourceDictType):
        self.check_conflict(module, resource, data)
        db_cfg_by_module_resource[(module, resource)] = ConfiguredDB(
            module, resource, data
        )

        abs_fn = filename_for_file_resource(module, data["database_file"])
        os.makedirs(os.path.dirname(abs_fn), exist_ok=True)
        db = Database(datasette_instance, abs_fn, is_mutable=True, mode="rwc")

        db_cfg_by_module_resource[(module, resource)].db = db

        db_cfg_by_datasette_id[data["database_name"]] = db_cfg_by_module_resource[
            (module, resource)
        ]

        datasette_instance.add_database(db, data["database_name"])

    def on_delete(self, module, resource: str, data):
        to_rm = None
        for i in db_cfg_by_module_resource:
            if db_cfg_by_module_resource[i].id == (module, resource):
                to_rm = i
                break
        if to_rm:
            del db_cfg_by_module_resource[to_rm]

        try:
            datasette_instance.remove_database(data["database_name"])
        except Exception:
            pass

    def on_update(self, module: str, resource: str, data: ResourceDictType):
        self.on_delete(module, resource, data)
        self.on_load(module, resource, data)

    def on_create_request(self, module, resource, kwargs):
        self.check_conflict(module, resource, kwargs)
        d = {"resource_type": self.type}
        d.update(kwargs)
        d.pop("name")
        d.pop("Save", None)

        if not d["database_name"]:
            raise Exception("Database name required")

        if not d["database_file"]:
            raise Exception("Database file required")

        return d

    def on_update_request(self, module, resource, data: ResourceDictType, kwargs):
        self.check_conflict(module, resource, kwargs)
        d: dict[str, Any] = mutable_copy_resource(data)
        d.update(kwargs)
        d.pop("Save", None)
        return d

    def create_page(self, module, path):
        d = dialogs.SimpleDialog("New Datasette Database")
        d.text_input("name", title="Resouce name", default="my_db")

        d.text_input(
            "database_name",
            default="my_db",
            title="Database Name (must be unique) in main Datasette listing",
        )

        d.text_input(
            "database_file",
            default="my_db.db",
            title="Database File(Relative paths start in the module)",
        )

        d.text_input(
            "read_perms",
            title="Read Permissions",
            default="system.admin",
        )

        d.text_input(
            "write_perms",
            title="Write Permissions",
            default="system.admin",
        )
        d.submit_button("Save")
        return d.render(self.get_create_target(module, path))

    def edit_page(self, module, resource, data):
        d = dialogs.SimpleDialog("Editing Datasette Database")

        d.text_input(
            "database_name",
            title="Database Name in main Datasette listing",
            default=data["database_name"],
        )

        d.text_input(
            "database_file",
            title="Database File",
            default=data["database_file"],
        )

        d.text_input(
            "read_perms",
            title="Read Permissions",
            default=data["read_perms"],
        )

        d.text_input(
            "write_perms",
            title="Write Permissions",
            default=data["write_perms"],
        )

        d.submit_button("Save")
        return d.render(self.get_update_target(module, resource))


drt = DatasetteResourceType("datasette", mdi_icon="database")
resource_types["datasette"] = drt
