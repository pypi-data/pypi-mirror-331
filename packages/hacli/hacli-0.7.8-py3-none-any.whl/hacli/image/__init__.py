import typer

from . import (
    check_service_image_imported,
    import_global_external_images,
    import_global_service_images,
    purge_local_images
)
from ..deploy import check_services_deployment_status

app = typer.Typer()

app.add_typer(check_service_image_imported.app)
app.add_typer(check_services_deployment_status.app)
app.add_typer(import_global_external_images.app)
app.add_typer(import_global_service_images.app)
app.add_typer(purge_local_images.app)
