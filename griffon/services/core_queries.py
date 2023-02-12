"""
    read only queries

"""
import concurrent
import logging
from typing import Any, Dict, List

from griffon import CORGI_API_URL, OSIDB_API_URL, CorgiService, OSIDBService

logger = logging.getLogger("rich")


class products_versions_affected_by_specific_cve_query:
    """Given a specific CVE ID, what products are affected?"""

    name = "product-versions-affected-by-specific-cve"
    description = "Given a specific CVE ID, what product versions are affected?"
    allowed_params = ["cve_id"]

    def __init__(self, params: dict) -> None:
        self.osidb_session = OSIDBService.create_session()
        self.params = params

    def execute(self) -> dict:
        cve_id = self.params["cve_id"]
        flaw = self.osidb_session.flaws.retrieve(cve_id)
        pv_names = list()
        for affect in flaw.affects:
            pv_names.append(affect.ps_module)
        pv_names = list(set(pv_names))
        product_versions = list()
        for pv_name in pv_names:
            product_versions.append(
                {
                    "link": f"{CORGI_API_URL}/api/v1/product_versions?name={pv_name}",
                    "name": pv_name,
                }
            )
        return {
            "link": f"{OSIDB_API_URL}/osidb/api/v1/flaws/{cve_id}",
            "cve_id": cve_id,
            "title": flaw.title,
            "description": flaw.description,
            "product_versions": product_versions,
        }


class products_containing_specific_component_query:
    """What products contain a specific component?"""

    name = "products_containing_specific_component_query"
    description = "What products contain a specific component?"
    allowed_params = ["component_name", "purl", "namespace"]

    def __init__(self, params: dict) -> None:
        self.corgi_session = CorgiService.create_session()
        self.params = params

    def execute(self) -> dict:
        purl = self.params["purl"]
        c = self.corgi_session.components.retrieve_list(
            purl=purl,
        )
        return c["product_streams"]


class products_containing_component_query:
    """What products contain a component?"""

    name = "products_containing_component_query"
    description = "What products contain a component?"
    allowed_params = ["component_name", "purl", "namespace"]

    def __init__(self, params: dict) -> None:
        self.corgi_session = CorgiService.create_session()
        self.params = params

    def execute(self) -> List[Dict[str, Any]]:
        component_name = self.params["component_name"]
        namespace = self.params["namespace"]
        cond = {}
        cond["name"] = component_name
        if namespace:
            cond["namespace"] = namespace
        components = self.corgi_session.components.retrieve_list(
            **cond,
            view="product",
        )
        results = []
        for c in components.results:
            results.append(
                {
                    "link": c.link,
                    "ofuri": c["ofuri"],
                    "name": c.name,
                    "component_link": c["component_link"],
                    "component_purl": c["component_purl"],
                }
            )
        return results


class product_stream_summary:
    """retrieve product_stream summary"""

    name = "product_stream_summary"
    description = "retrieve product_stream summary"
    allowed_params = ["product_stream_name", "ofuri", "inactive"]

    def __init__(self, params: dict) -> None:
        self.corgi_session = CorgiService.create_session()
        self.params = params

    def execute(self) -> dict:
        cond = {}
        product_stream_name = self.params["product_stream_name"]
        ofuri = self.params["ofuri"]
        if product_stream_name:
            cond["name"] = product_stream_name
        if ofuri:
            cond["ofuri"] = ofuri
        # TODO - corgi bindings need to support ofuri in product_streams
        product_stream = self.corgi_session.product_streams.retrieve_list(**cond)
        components_cnt = self.corgi_session.components.retrieve_list(
            ofuri=product_stream["ofuri"], view="summary", limit=1
        ).count
        return {
            "link": product_stream["link"],
            "ofuri": product_stream["ofuri"],
            "name": product_stream["name"],
            "product": product_stream["products"][0]["name"],
            "product_version": product_stream["product_versions"][0]["name"],
            "brew_tags": list(product_stream["brew_tags"].keys()),
            "build_count": product_stream["build_count"],
            "latest_component_count": components_cnt,
            "manifest_link": product_stream["manifest"],
            "shipped_components_link": "tbd",
            "latest_components_link": product_stream["components"],
            "all_components_link": f"{CORGI_API_URL}/api/v1/components?product_streams={product_stream['ofuri']}&include_fields=link,name,purl",  # noqa
        }


class components_containing_specific_component_query:
    """What components contain a specific component?"""

    name = "components_containing_specific_component_query"
    description = "What components contain a specific component?"
    allowed_params = ["component_name", "purl", "component_type", "namespace"]

    def __init__(self, params: dict):
        self.corgi_session = CorgiService.create_session()
        self.params = params

    def execute(self) -> dict:
        purl = self.params["purl"]
        if purl:
            c = self.corgi_session.components.retrieve_list(
                purl=purl,
            )
            component_type = self.params["component_type"]
            sources = c["sources"]
            if component_type:
                sources = [source for source in sources if component_type.lower() in source["purl"]]
        return {
            "link": c["link"],
            "type": component_type,
            "name": c["name"],
            "purl": c["purl"],
            "sources": sources,
        }


class components_containing_component_query:
    """What components contain a component?"""

    name = "components_containing_component_query"
    description = "What components contain a component?"
    allowed_params = ["component_name", "purl", "component_type", "namespace"]

    def __init__(self, params: dict) -> None:
        self.corgi_session = CorgiService.create_session()
        self.params = params

    def execute(self) -> List[Dict[str, Any]]:
        component_type = self.params["component_type"]
        component_name = self.params["component_name"]
        namespace = self.params["namespace"]

        cond = {}
        cond["name"] = component_name
        if namespace:
            cond["namespace"] = namespace

        components = self.corgi_session.components.retrieve_list(
            **cond, limit=10000, include_fields="link,name,purl,sources"
        )
        results = []
        for c in components.results:
            sources = []
            for source in c.sources:
                sources.append({"link": source["link"], "purl": source["purl"]})
            if component_type:
                sources = [source for source in sources if component_type.lower() in source["purl"]]
            results.append(
                {
                    "link": c.link,
                    "name": c.name,
                    "purl": c.purl,
                    "sources": sources,
                }
            )
        return results


class components_affected_by_specific_cve_query:
    """Given a specific CVE ID, what components are affected?"""

    name = "components_affected_by_specific_cve_query"
    description = "Given a CVE ID, what components are affected?"
    allowed_params = [
        "cve_id",
        "affectedness",
        "affect_resolution",
        "affect_impact",
        "component_type",
        "namespace",
    ]

    def __init__(self, params: dict) -> None:
        self.corgi_session = CorgiService.create_session()
        self.osidb_session = OSIDBService.create_session()
        self.params = params

    def execute(self) -> dict:
        cve_id = self.params["cve_id"]
        affectedness = self.params["affectedness"]
        affect_resolution = self.params["affect_resolution"]
        affect_impact = self.params["affect_impact"]
        cond = {}
        if affectedness:
            cond["affectedness"] = affectedness
        if affect_resolution:
            cond["resolution"] = affect_resolution
        if affect_impact:
            cond["impact"] = affect_impact
        component_type = self.params["component_type"]
        namespace = self.params["namespace"]
        component_cond = {}
        if namespace:
            component_cond["namespace"] = namespace
        if component_type:
            component_cond["type"] = component_type
        flaw = self.osidb_session.flaws.retrieve(cve_id)
        affects = self.osidb_session.affects.retrieve_list(
            flaw=flaw.uuid, **cond, limit=1000
        ).results
        results = list()
        for affect in affects:
            try:
                product_version = self.corgi_session.product_versions.retrieve_list(
                    name=affect.ps_module
                ).results[0]
                components = []
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    futures = []
                    for ps in product_version.product_streams:
                        futures.append(
                            executor.submit(
                                self.corgi_session.components.retrieve_list,
                                **component_cond,
                                ofuri=ps["ofuri"],
                                name=affect.ps_component,
                                include_fields="link,purl,name,type",
                                limit=50000,
                            )
                        )
                    for future in concurrent.futures.as_completed(futures):
                        try:
                            for c in future.result().results:
                                components.append(c.to_dict())
                        except Exception as exc:
                            logger.error("%r generated an exception: %s" % (future, exc))
                            exit(0)

                results.append(
                    {
                        "link": f"{OSIDB_API_URL}/osidb/api/v1/affects/{affect.uuid}",
                        "product_version_name": affect.ps_module,
                        "component_name": affect.ps_component,
                        "affectedness": affect.affectedness,
                        "affect_impact": affect.impact,
                        "affect_resolution": affect.resolution,
                        "components": components,
                    }
                )
            except IndexError as err:
                logger.info(f"product stream not in component-registry: {err}")

        return {
            "link": f"{OSIDB_API_URL}/osidb/api/v1/flaws/{flaw.cve_id}",
            "cve_id": flaw.cve_id,
            "title": flaw.title,
            "description": flaw.description,
            "affects": results,
        }
