import traceback
import csv
import io

from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
import click
import tableauserverclient as TSC
from tableauhyperapi import (
    HyperProcess,
    Telemetry,
    Connection,
    CreateMode,
    TableName,
    HyperException,
)

from .cli_utils import load_config, authenticate, retry_on_exception
from .logging_config import configure_logging, get_logger
from .exception_handler import exception_handler


# Configure logging for this module
configure_logging(output_dir="output", module_name=__name__)
logger = get_logger(__name__)


@click.group()
def update():
    """Update various Tableau resources"""


@update.group()
def groups():
    """Update group attributes"""


@groups.command()
@click.option("--file", type=click.Path(exists=True), help="Path to the CSV file")
@click.option(
    "--input-hyper", type=click.Path(exists=True), help="Path to the .hyper file"
)
@click.option("--stdin", is_flag=True, help="Read from stdin instead of a file")
@click.option("--delimiter", default="\t", help="Delimiter used in the CSV file")
@click.option("--site-luid-col", default="site_luid", help="Column name for Site LUID")
@click.option(
    "--group-luid-col", default="object_luid", help="Column name for Group LUID"
)
@click.option(
    "--threads", default=1, type=int, help="Number of concurrent threads for updates"
)
@click.option(
    "--check-pattern",
    is_flag=True,
    default=False,
    help="Check for creator, explorer, viewer in group name for min site role",
)
@click.option(
    "--val-col",
    default=None,
    help="Column name containing the site_role values to use",
)
@click.option(
    "--literal-value",
    help="site_role value to set",
)
@click.pass_context
def minimum_site_role(
    ctx,
    file,
    input_hyper,
    stdin,
    delimiter,
    site_luid_col,
    group_luid_col,
    threads,
    check_pattern,
    val_col,
    literal_value,
):
    """Update user site roles"""
    update_group_attribute(
        ctx,
        file,
        input_hyper,
        stdin,
        delimiter,
        site_luid_col,
        group_luid_col,
        val_col,
        "minimum_site_role",
        threads,
        check_pattern,
        literal_value,
    )


@exception_handler
def update_group_attribute(
    ctx,
    file,
    input_hyper,
    stdin,
    delimiter,
    site_luid_col,
    group_luid_col,
    val_col,
    attribute,
    threads,
    check_pattern,
    literal_value=None,
):

    config = load_config(ctx.obj["config"])
    server = authenticate(config)
    csv_data = get_data(file, input_hyper, stdin, delimiter)

    # Group data by site
    site_groups = defaultdict(list)
    for row in csv_data:
        site_luid = row[site_luid_col]
        site_groups[site_luid].append(row)

    @exception_handler
    def update_group(
        server: TSC.Server, site, group_luid, new_value, attribute, check_pattern
    ):
        try:
            group = [
                group for group in TSC.Pager(server.groups) if group.id == group_luid
            ]

            if group:
                group = group[0]
            else:
                logger.warning(
                    "Group not found",
                    attribute=attribute,
                    group_name=group.name,
                    group_luid=group_luid,
                    site_name=site.name,
                    site_id=site.id,
                )
                return

            if check_pattern:
                group_name_lower = group.name.lower()
                if "creator" in group_name_lower:
                    new_value = "Creator"
                elif "explorer" in group_name_lower:
                    new_value = "Explorer"
                elif "viewer" in group_name_lower:
                    new_value = "Viewer"

            setattr(group, attribute, new_value)
            server.groups.update(group)
            logger.info(
                "Group attribute updated",
                attribute=attribute,
                new_value=new_value,
                group_name=group.name,
                group_luid=group_luid,
                site_name=site.name,
                site_id=site.id,
            )
            return f"Updated {attribute} for group {group.name} ({group_luid}) on site {site.name} ({site.id})"
        except (
            Exception,
            TSC.ServerResponseError,
            ValueError,
            TypeError,
            AttributeError,
        ) as e:
            logger.error("Error updating group", group_luid=group_luid, error=str(e))
            return f"Error updating group {group_luid}: {str(e)}"

    site_map = {site.id: site for site in TSC.Pager(server.sites)}
    for site_luid, site_data in site_groups.items():
        try:
            site = site_map[site_luid]
            server.auth.switch_site(site)
            logger.info(f"switched to site: {site.name}")

            with ThreadPoolExecutor(max_workers=threads) as executor:
                futures = [
                    executor.submit(
                        update_group,
                        server,
                        site,
                        row[group_luid_col],
                        literal_value if literal_value is not None else row[val_col],
                        attribute,
                        check_pattern,
                    )
                    for row in site_data
                ]
                for future in as_completed(futures):
                    result = future.result()
                    logger.info(result)
        except (ValueError, TypeError, AttributeError) as e:
            logger.exception(f"Error processing site: {e}", site_luid=site_luid)
    server.auth.sign_out()


@update.group()
def users():
    """Update user attributes"""


@users.command()
@click.option("--file", type=click.Path(exists=True), help="Path to the CSV file")
@click.option(
    "--input-hyper", type=click.Path(exists=True), help="Path to the .hyper file"
)
@click.option("--stdin", is_flag=True, help="Read from stdin instead of a file")
@click.option("--delimiter", default="\t", help="Delimiter used in the CSV file")
@click.option("--site-luid-col", default="site_luid", help="Column name for Site LUID")
@click.option(
    "--user-luid-col", default="object_luid", help="Column name for User LUID"
)
@click.option(
    "--val-col",
    default="object_email",
    help="Column name containing the email values to use",
)
@click.option(
    "--threads", default=1, type=int, help="Number of concurrent threads for updates"
)
@click.pass_context
def email(
    ctx,
    file,
    input_hyper,
    stdin,
    delimiter,
    site_luid_col,
    user_luid_col,
    val_col,
    threads,
):
    """Update user email addresses"""
    update_user_attribute(
        ctx,
        file,
        input_hyper,
        stdin,
        delimiter,
        site_luid_col,
        user_luid_col,
        val_col,
        "email",
        threads,
    )


@retry_on_exception(max_attempts=3, delay=2)
def _update_group(server: TSC.Server, group_obj):
    return server.groups.update(group_obj)


@users.command()
@click.option("--file", type=click.Path(exists=True), help="Path to the CSV file")
@click.option(
    "--input-hyper", type=click.Path(exists=True), help="Path to the .hyper file"
)
@click.option("--stdin", is_flag=True, help="Read from stdin instead of a file")
@click.option("--delimiter", default="\t", help="Delimiter used in the CSV file")
@click.option("--site-luid-col", default="site_luid", help="Column name for Site LUID")
@click.option(
    "--user-luid-col", default="object_luid", help="Column name for User LUID"
)
@click.option(
    "--threads", default=1, type=int, help="Number of concurrent threads for updates"
)
@click.option(
    "--val-col",
    default=None,
    help="Column name containing the site_role values to use",
)
@click.option(
    "--literal-value",
    help="site_role value to set",
)
@click.pass_context
def site_role(
    ctx,
    file,
    input_hyper,
    stdin,
    delimiter,
    site_luid_col,
    user_luid_col,
    threads,
    val_col,
    literal_value,
):
    """Update user site roles"""
    update_user_attribute(
        ctx,
        file,
        input_hyper,
        stdin,
        delimiter,
        site_luid_col,
        user_luid_col,
        val_col,
        "site_role",
        threads,
        literal_value,
    )


@exception_handler
def update_user_attribute(
    ctx,
    file,
    input_hyper,
    stdin,
    delimiter,
    site_luid_col,
    user_luid_col,
    val_col,
    attribute,
    threads,
    literal_value=None,
):
    config = load_config(ctx.obj["config"])
    server = authenticate(config)

    csv_data = get_data(file, input_hyper, stdin, delimiter)

    # Group data by site
    site_groups = defaultdict(list)
    for row in csv_data:
        site_luid = row[site_luid_col]
        site_groups[site_luid].append(row)

    @exception_handler
    def update_user(server: TSC.Server, site, user_luid, new_value, attribute):
        try:
            user = server.users.get_by_id(user_luid)
            setattr(user, attribute, new_value)
            server.users.update(user)
            logger.info(
                "User attribute updated",
                attribute=attribute,
                user_name=user.name,
                user_luid=user_luid,
                site_name=site.name,
                site_id=site.id,
            )
            return f"Updated {attribute} for user {user.name} ({user_luid}) on site {site.name} ({site.id})"
        except (
            Exception,
            TSC.ServerResponseError,
            ValueError,
            TypeError,
            AttributeError,
        ) as e:
            logger.error("Error updating user", user_luid=user_luid, error=str(e))
            return f"Error updating user {user_luid}: {str(e)}, traceback: {traceback.format_exc()}"

    site_map = {site.id: site for site in TSC.Pager(server.sites)}
    for site_luid, site_data in site_groups.items():
        try:
            site = site_map[site_luid]
            server.auth.switch_site(site)
            logger.info(f"switched to site: {site.name}")

            with ThreadPoolExecutor(max_workers=threads) as executor:
                futures = [
                    executor.submit(
                        update_user,
                        server,
                        site,
                        row[user_luid_col],
                        literal_value if literal_value is not None else row[val_col],
                        attribute,
                    )
                    for row in site_data
                ]
                for future in as_completed(futures):
                    result = future.result()
                    logger.info(result)
        except (ValueError, TypeError, AttributeError) as e:
            logger.exception(f"Error processing site: {e}", site_luid=site_luid)
    server.auth.sign_out()


def get_data(csv_file, hyper_file, use_stdin, delimiter):
    """
    Reads data from either a CSV file, a Tableau Hyper file, or stdin.
    Only one source can be specified at a time.
    """

    # Check for mutually exclusive options
    num_sources = sum([csv_file is not None, hyper_file is not None, use_stdin])
    if num_sources > 1:
        raise click.UsageError(
            "Only one of --file, --input-hyper, or --stdin can be specified."
        )

    if hyper_file:
        return get_hyper_data(hyper_file)

    if csv_file:
        return get_csv_data(csv_file, False, delimiter)  # Modified call

    if use_stdin:
        return get_csv_data(None, True, delimiter)  # Modified call

    raise click.UsageError("You must specify one of --file, --input-hyper, or --stdin.")


def get_csv_data(file, use_stdin, delimiter):
    """Reads data from a CSV file or stdin."""
    if file and use_stdin:
        raise click.UsageError("Cannot use both --file and --stdin.")

    if use_stdin:
        input_stream = io.TextIOWrapper(
            click.get_binary_stream("stdin"), encoding="utf-8"
        )
        reader = csv.DictReader(input_stream, delimiter=delimiter)
        return list(reader)
    if file:
        with open(file, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=delimiter)
            return list(reader)
    else:
        raise click.UsageError("You must specify either --file or --stdin.")


def get_hyper_data(hyper_file):
    """Reads data from a Tableau Hyper file."""
    try:
        with HyperProcess(Telemetry.DO_NOT_SEND_USAGE_DATA_TO_TABLEAU) as hyper:
            with Connection(hyper.endpoint, hyper_file, CreateMode.NONE) as connection:
                table_name = TableName("public", "Extract")

                # Fetch all rows from the .hyper file
                select_statement = f"SELECT * FROM {table_name}"
                result = connection.execute_list_query(select_statement)

                # column names from cursor description
                column_names = [
                    desc.name.unescaped
                    for desc in connection.catalog.get_table_definition(
                        table_name
                    ).columns
                ]
                data = []
                for row in result:
                    data.append(dict(zip(column_names, row)))
        return data
    except (HyperException, FileNotFoundError) as e:
        raise click.ClickException(f"Error reading data from .hyper file: {e}")
