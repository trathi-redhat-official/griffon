"""

"""
import concurrent.futures
import logging

import click

from griffon import CORGI_API_URL, OSIDB_API_URL, CorgiService, OSIDBService
from griffon.autocomplete import get_product_stream_names, get_product_stream_ofuris
from griffon.output import console, cprint

logger = logging.getLogger("rich")

default_conditions: dict = {}


@click.group(name="entities", help="List and retrieve entities operations.")
@click.option("--open-browser", is_flag=True)
@click.option("--limit", default=10)
@click.pass_context
def entities_grp(ctx, open_browser, limit):
    ctx.ensure_object(dict)
    ctx.obj["open_browser"] = open_browser
    ctx.obj["limit"] = limit


# flaws
@entities_grp.group(help=f"{OSIDB_API_URL}/osidb/api/v1/flaws")
@click.pass_context
def flaws(ctx):
    """OSIDB Flaws."""


@flaws.command(name="list")
@click.option(
    "--state",
    "flaw_state",
    type=click.Choice(OSIDBService.get_flaw_states()),
)
@click.option(
    "--resolution",
    type=click.Choice(OSIDBService.get_flaw_resolutions()),
)
@click.option("--impact", type=click.Choice(OSIDBService.get_flaw_impacts()))
@click.option("--embargoed", "is_embargoed", is_flag=True)
@click.option("--major-incident", "is_major_incident", is_flag=True)
@click.pass_context
def list_flaws(ctx, flaw_state, resolution, impact, is_embargoed, is_major_incident):
    if not flaw_state and not resolution and not impact:
        click.echo(ctx.get_help())
        exit(0)
    with console.status("griffoning...", spinner="line"):
        session = OSIDBService.create_session()
        conditions = default_conditions
        if flaw_state:
            conditions["state"] = flaw_state
        if resolution:
            conditions["resolution"] = resolution
        if impact:
            conditions["impact"] = impact
        data = session.flaws.retrieve_list(**conditions).results
        return cprint(data, ctx=ctx)


@flaws.command(name="get")
@click.option("--cve-id")
@click.option("--uuid", "flaw_uuid")
@click.pass_context
def get_flaw(ctx, cve_id, flaw_uuid):
    if not cve_id and not flaw_uuid:
        click.echo(ctx.get_help())
        exit(0)
    with console.status("griffoning...", spinner="line"):
        session = OSIDBService.create_session()
        if flaw_uuid:
            data = session.flaws.retrieve(flaw_uuid)
        if cve_id:
            data = session.flaws.retrieve(cve_id)
        return cprint(data, ctx=ctx)


# affects
@entities_grp.group(help=f"{OSIDB_API_URL}/osidb/api/v1/affects")
@click.pass_context
def affects(ctx):
    """OSIDB Affects."""
    pass


@affects.command(name="list")
@click.option("--product_version", help="ps module")
@click.option("--component_name", help="ps component")
@click.option("--affectedness", type=click.Choice(OSIDBService.get_affect_affectedness()))
@click.option(
    "--resolution",
    type=click.Choice(OSIDBService.get_affect_resolution()),
)
@click.option("--impact", type=click.Choice(OSIDBService.get_affect_impact()))
@click.pass_context
def list_affects(ctx, product_version, component_name, affectedness, resolution, impact):
    if (
        not product_version
        and not component_name
        and not affectedness
        and not resolution
        and not impact
    ):
        click.echo(ctx.get_help())
        exit(0)
    with console.status("griffoning...", spinner="line"):
        session = OSIDBService.create_session()
        conditions = default_conditions
        if product_version:
            conditions["ps_module"] = product_version
        if component_name:
            conditions["ps_component"] = component_name
        if affectedness:
            conditions["affectedness"] = affectedness
        if resolution:
            conditions["resolution"] = resolution
        if impact:
            conditions["impact"] = impact
        data = session.affects.retrieve_list(**conditions).results
        return cprint(data, ctx=ctx)


@affects.command(name="get")
@click.option("--uuid", "affect_uuid")
@click.pass_context
def get_affect(ctx, affect_uuid):
    if not affect_uuid:
        click.echo(ctx.get_help())
        exit(0)
    with console.status("griffoning...", spinner="line"):
        session = OSIDBService.create_session()
        data = session.affects.retrieve(affect_uuid)
        return cprint(data, ctx=ctx)


# trackers
@entities_grp.group(help=f"{OSIDB_API_URL}/osidb/api/v1/trackers")
@click.pass_context
def trackers(ctx):
    """OSIDB Trackers."""
    pass


@trackers.command(name="list")
@click.pass_context
def list_trackers(ctx):
    with console.status("griffoning...", spinner="line"):
        session = OSIDBService.create_session()
        conditions = default_conditions
        data = session.trackers.retrieve_list(**conditions).results
        return cprint(data, ctx=ctx)


@trackers.command(name="get")
@click.option("--uuid", "tracker_uuid")
@click.pass_context
def get_tracker(ctx, tracker_uuid):
    if not tracker_uuid:
        click.echo(ctx.get_help())
        exit(0)
    with console.status("griffoning...", spinner="line"):
        session = OSIDBService.create_session()
        data = session.trackers.retrieve(tracker_uuid)
        return cprint(data, ctx=ctx)


# components
@entities_grp.group(help=f"{CORGI_API_URL}/api/v1/components")
@click.pass_context
def components(ctx):
    pass


@components.command(name="list")
@click.option("--namespace", type=click.Choice(CorgiService.get_component_namespaces()), help="")
@click.option("--ofuri")
@click.option("--product-stream-name")
@click.option("--re_purl")
@click.option("--name")
@click.option("--re_name")
@click.option("--version")
@click.option(
    "--type",
    "component_type",
    type=click.Choice(CorgiService.get_component_types()),
    help="",  # noqa
)
@click.option(
    "--arch",
    type=click.Choice(CorgiService.get_component_arches()),
)
@click.option("--view", default="summary")
@click.pass_context
def list_components(
    ctx,
    namespace,
    ofuri,
    product_stream_name,
    re_purl,
    name,
    re_name,
    version,
    component_type,
    arch,
    view,
):
    """Retrieve a list of components."""

    if (
        not ofuri
        and not re_purl
        and not name
        and not re_name
        and not version
        and not arch
        and not namespace
        and not component_type
    ):
        click.echo(ctx.get_help())
        exit(0)
    with console.status("griffoning...", spinner="line"):
        session = CorgiService.create_session()

        conditions = default_conditions
        conditions["view"] = view

        # TODO- condition union could be a separate helper function

        if namespace:
            conditions["namespace"] = namespace
        if ofuri:
            conditions["ofuri"] = ofuri
        if re_purl:
            conditions["re_purl"] = re_purl
        if name:
            conditions["name"] = name
        if re_name:
            conditions["re_name"] = re_name
        if version:
            conditions["version"] = version
        if arch:
            conditions["arch"] = arch

        # TODO- This kind of optimisation should probably be developed in the
        #       service binding itself rather then here
        logger.debug("starting parallel http requests")
        component_cnt = session.components.retrieve_list(**conditions).count
        if component_cnt < 50000:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []
                components = list()
                for batch in range(0, component_cnt, 1200):
                    futures.append(
                        executor.submit(
                            session.components.retrieve_list,
                            **conditions,
                            offset=batch,
                            limit=1200,  # noqa
                        )
                    )

                for future in concurrent.futures.as_completed(futures):
                    try:
                        components.extend(future.result().results)
                    except Exception as exc:
                        logger.info("%r generated an exception: %s" % (future, exc))
                        exit(0)

                data = sorted(components, key=lambda d: d.purl)
                return cprint(data, ctx=ctx)
        else:
            console.print("downloading too many")


@components.command(name="get")
@click.option("--uuid", "component_uuid")
@click.option("--purl")
@click.option("--nvr")
@click.pass_context
def get_component(ctx, component_uuid, purl, nvr):
    """Retrieve a specific component."""
    if not component_uuid and not purl and not nvr:
        click.echo(ctx.get_help())
        exit(0)
    with console.status("griffoning...", spinner="line"):
        session = CorgiService.create_session()
        data = session.components.retrieve_list(purl=purl)
        return cprint(data, ctx=ctx)


@components.command(name="get-manifest")
@click.option("--uuid", "component_uuid")
@click.option("--purl")
@click.pass_context
def get_component_manifest(ctx, component_uuid, purl):
    """Retrieve a specific component."""
    if not component_uuid and not purl:
        click.echo(ctx.get_help())
        exit(0)
    with console.status("griffoning...", spinner="line"):
        session = CorgiService.create_session()
        if component_uuid:
            data = session.components.retrieve_manifest(component_uuid)
            return cprint(data, ctx=ctx)
        else:
            c = session.components.retrieve_list(purl=purl)
            if c:
                data = session.components.retrieve_manifest(c["uuid"])
                return cprint(data, ctx=ctx)


# product streams
@entities_grp.group(help=f"{CORGI_API_URL}/api/v1/product_streams")
@click.pass_context
def product_streams(ctx):
    pass


@product_streams.command(name="list")
@click.option("--inactive", is_flag=True, default=False, help="Show inactive project streams")
@click.option("--re-name", "re_name", type=click.STRING, shell_complete=get_product_stream_names)
@click.pass_context
def list_product_streams(ctx, inactive, re_name):
    """Retrieve a list of product_streams."""
    with console.status("griffoning...", spinner="line"):
        session = CorgiService.create_session()
        cond = default_conditions
        if re_name:
            cond["re_name"] = re_name
        data = session.product_streams.retrieve_list(**cond).results
        return cprint(data, ctx=ctx)


@product_streams.command(name="get")
@click.option("--inactive", is_flag=True, default=False, help="Show inactive project streams")
@click.option("--ofuri", "ofuri", type=click.STRING, shell_complete=get_product_stream_ofuris)
@click.option(
    "--name", "product_stream_name", type=click.STRING, shell_complete=get_product_stream_names
)
@click.pass_context
def get_product_stream(ctx, inactive, ofuri, product_stream_name):
    """Retrieve a specific product_stream."""
    if not ofuri and not product_stream_name:
        click.echo(ctx.get_help())
        exit(0)
    with console.status("griffoning...", spinner="line"):
        session = CorgiService.create_session()
        cond = {}
        if ofuri:
            cond["ofuri"] = ofuri
        if product_stream_name:
            cond["name"] = product_stream_name
        data = session.product_streams.retrieve_list(**cond)
        return cprint(data, ctx=ctx)


@product_streams.command(name="get-latest-components")
@click.option("--namespace", type=click.Choice(CorgiService.get_component_namespaces()), help="")
@click.option("--ofuri", "ofuri", type=click.STRING, shell_complete=get_product_stream_ofuris)
@click.option(
    "--name", "product_stream_name", type=click.STRING, shell_complete=get_product_stream_names
)
@click.option("--view", default="summary")
@click.pass_context
def get_product_stream_components(ctx, namespace, ofuri, product_stream_name, view):
    """Retrieve a specific product_stream."""
    if not ofuri and not product_stream_name:
        click.echo(ctx.get_help())
        exit(0)
    ctx.invoke(list_components, ofuri=ofuri)


@product_streams.command(name="get-manifest")
@click.option("--ofuri", "ofuri", type=click.STRING, shell_complete=get_product_stream_ofuris)
@click.option(
    "--name", "product_stream_name", type=click.STRING, shell_complete=get_product_stream_names
)
@click.pass_context
def get_product_stream_manifest(ctx, ofuri, product_stream_name):
    """Retrieve a product_stream manifest."""
    if not ofuri and not product_stream_name:
        click.echo(ctx.get_help())
        exit(0)
    with console.status("griffoning...", spinner="line"):
        session = CorgiService.create_session()
        pv = None
        if ofuri:
            pv = session.product_streams.retrieve_list(ofuri=ofuri).additional_properties
        if product_stream_name:
            pv = session.product_streams.retrieve_list(
                name=product_stream_name
            ).additional_properties
        if pv:
            data = session.product_streams.retrieve_manifest(pv["uuid"])
            return cprint(data, ctx=ctx)
