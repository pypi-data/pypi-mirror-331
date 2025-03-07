# dto_to_stac.py
import logging
import os.path
from datetime import datetime, timezone
from typing import Any, Dict, List

import pystac
import shapely

from odp.client import OdpClient
from odp.dto import DataCollectionDto, DatasetDto, ObservableDto, ResourceDto
from odp.dto.registry.observables_class_definitions import (
    static_coverage_class,
    static_geometric_coverage_class,
    static_single_value_class,
)
from odp.stac import CATALOG_FRONTEND_URL, STAC_API_URL


def get_root_catalog() -> pystac.Catalog:
    root_catalog = pystac.Catalog(id="stac-root", description="Hub Ocean Public STAC API", href=STAC_API_URL)

    # Collections link
    root_catalog.add_link(
        pystac.Link(
            rel="data",
            target=os.path.join(STAC_API_URL, "collections"),
            media_type=pystac.MediaType.JSON,
        )
    )
    # Search link
    root_catalog.add_link(
        pystac.Link(
            rel="search",
            target=os.path.join(STAC_API_URL, "search"),
            media_type=pystac.MediaType.JSON,
        )
    )

    # Link to webview for catalog
    root_catalog.add_link(
        pystac.Link(
            rel=pystac.RelType.ALTERNATE,
            target=CATALOG_FRONTEND_URL,
            media_type=pystac.MediaType.HTML,
            title="Hub Ocean Web Catalog",
        )
    )
    return root_catalog


def get_observables(dto: ResourceDto, odp_client: OdpClient) -> List[ObservableDto]:
    """
    Get observables associated with a dataset.
    """
    try:
        observables = odp_client.catalog.list(
            {"#AND": [{"#EQUALS": ["kind", ObservableDto.get_kind()]}, {"#EQUALS": ["$spec.ref", dto.qualified_name]}]}
        )
    except Exception as e:
        logging.info(f"Error fetching observables for dataset {dto.uuid}: {e}")
        observables = []

    return list(observables)


class ObservablesInfo:
    start_time: datetime = None
    end_time: datetime = None
    geometry: Dict[str, Any] = None
    bbox: List[float] = None
    time: datetime = None

    def add_observable(self, observable: ObservableDto):
        if observable.spec.observable_class == static_coverage_class.qualified_name:
            try:
                self.start_time = datetime.fromtimestamp(observable.spec.details["value"][0])
                self.end_time = datetime.fromtimestamp(observable.spec.details["value"][1])
            except ValueError as e:
                logging.info(f"Error parsing observable {observable.uuid}: {e}")
                raise
        elif observable.spec.observable_class == static_single_value_class.qualified_name:
            try:
                value = observable.spec.details["value"]
                if isinstance(value, (int, float)):
                    self.time = datetime.fromtimestamp(value)
                else:
                    self.time = datetime.fromisoformat(value)
            except (ValueError, TypeError) as e:
                logging.info(f"Error parsing observable {observable.uuid}: {e}")
                raise ValueError(f"Error parsing observable {observable.uuid}: {e}")
        elif observable.spec.observable_class == static_geometric_coverage_class.qualified_name:
            try:
                self.geometry = observable.spec.details["value"]
                self.bbox = shapely.geometry.shape(self.geometry).bounds
            except shapely.errors.ShapelyError as e:
                logging.info(f"Error parsing observable {observable.uuid}: {e}")
                raise
        else:
            raise ValueError(f"Observable class {observable.spec.observable_class} not supported")

    def get_default_time(self) -> datetime:
        """Returns default time to current time if no time is available."""
        if self.start_time and self.end_time:
            return self.time
        elif self.time is None:
            return datetime.now(tz=timezone.utc)
        return self.time

    def get_temporal_extent(self) -> pystac.TemporalExtent:
        """Returns a pystac.TemporalExtent object based on the available time information."""
        if self.start_time and self.end_time:
            return pystac.TemporalExtent(intervals=[[self.start_time, self.end_time]])
        elif self.time:
            return pystac.TemporalExtent(intervals=[[self.time, None]])
        else:
            return pystac.TemporalExtent(intervals=[None, None])

    def get_spatial_extent(self) -> pystac.SpatialExtent:
        """Returns a pystac.SpatialExtent object based on the available spatial information.

        Defaults to the global extent if no spatial information is available.
        """
        if self.bbox:
            return pystac.SpatialExtent(bboxes=[self.bbox])
        return pystac.SpatialExtent(bboxes=[[-180, -90, 180, 90]])

    @classmethod
    def from_observables(cls, observables: List[ObservableDto]) -> "ObservablesInfo":
        info = cls()
        for observable in observables:
            try:
                info.add_observable(observable)
            except ValueError:
                continue
        return info


def convert_dataset(dto: DatasetDto) -> pystac.Item:
    """
    Converts a Dataset DTO to a STAC Item.
    """
    observables_info = ObservablesInfo.from_observables(dto.spec.observables)

    if dto.spec.data_collection is None:
        # Raise an error if the dataset does not belong to a collection. The
        # reason for this is that this stac api implementation assumes that all
        # items follow the format /collections/{collection_id}/items/{feature_id}
        raise AssertionError(f"Dataset does not belong to a collection: {dto}")

    dataset_identifier = dto.metadata.name
    collection_identifier = dto.spec.data_collection.split("/")[-1]

    dataset_api_url = os.path.join(STAC_API_URL, "collections", collection_identifier, "items", dataset_identifier)

    # Create a STAC Item
    item = pystac.Item(
        stac_extensions=[],
        href=dataset_api_url,
        id=str(dto.uuid),
        geometry=observables_info.geometry,
        bbox=observables_info.bbox,
        properties={},
        datetime=observables_info.get_default_time(),
        start_datetime=observables_info.start_time,
        end_datetime=observables_info.end_time,
        assets={},
        collection=dto.spec.data_collection,
    )

    # Add links
    # Set root object (this is to get the correct root link)
    item.set_root(get_root_catalog())

    # Add link to parent collection
    item.add_link(
        pystac.Link(
            rel=pystac.RelType.COLLECTION,
            target=os.path.join(STAC_API_URL, "collections", collection_identifier),
            title=collection_identifier,
            media_type=pystac.MediaType.JSON,
        )
    )

    # Link to webview for catalog
    item.add_link(
        pystac.Link(
            rel=pystac.RelType.ALTERNATE,
            target=os.path.join(CATALOG_FRONTEND_URL, "dataset", dataset_identifier),
            media_type=pystac.MediaType.HTML,
            title="Hub Ocean Web Catalog",
        )
    )

    # Validate STAC Item
    try:
        item.validate()
    except pystac.STACValidationError as e:
        logging.warning("Validation failed for DatasetDto %s converted to a STAC Item %s: %s", dto.uuid, item, e)
        raise

    return item


def convert_collection(dto: DataCollectionDto) -> pystac.Collection:
    """
    Converts a DataCollection DTO to a STAC Collection.
    """
    observables_info = ObservablesInfo.from_observables(dto.spec.observables)

    extent = pystac.Extent(
        spatial=observables_info.get_spatial_extent(),
        temporal=observables_info.get_temporal_extent(),
    )

    # Determine the license name (default to "proprietary")
    license_name = "proprietary"
    license_href = None

    if dto.spec.distribution and dto.spec.distribution.license:
        license_obj = dto.spec.distribution.license  # This is an instance of License

        def normalize_license(li_name):
            li_name = li_name.replace(" ", "_")
            li_name = li_name.replace("(", "")
            li_name = li_name.replace(")", "")
            return li_name

        license_name = normalize_license(license_obj.name or license_name)  # License name
        license_href = license_obj.href  # URL to license text

    collection_api_url = os.path.join(STAC_API_URL, "collections", dto.metadata.name)

    # Create pystac.Collection
    collection = pystac.Collection(
        id=str(dto.uuid),
        description=dto.metadata.description or "",
        href=collection_api_url,
        title=dto.metadata.name,
        license=license_name,
        extent=extent,
    )

    # Add links for collection
    # Set root object (this is to get the correct root link)
    collection.set_root(get_root_catalog())

    # Parent link
    collection.add_link(
        pystac.Link(
            rel=pystac.RelType.PARENT,
            target=os.path.join(STAC_API_URL, "collections"),
            media_type=pystac.MediaType.JSON,
        )
    )

    # Items link
    collection.add_link(
        pystac.Link(
            rel=pystac.RelType.ITEMS,
            target=os.path.join(collection_api_url, "items"),
            media_type=pystac.MediaType.JSON,
        )
    )

    # Link to webview for catalog
    collection.add_link(
        pystac.Link(
            rel=pystac.RelType.ALTERNATE,
            target=os.path.join(CATALOG_FRONTEND_URL, "collection", str(dto.metadata.name)),
            media_type=pystac.MediaType.HTML,
            title="Hub Ocean Web Catalog",
        )
    )

    # Add license link if href is available
    if license_href:
        collection.add_link(
            pystac.Link(
                rel="license",
                target=license_href,
                title=f"License: {license_name}",
            )
        )

    # Validate STAC collection
    try:
        collection.validate()
    except pystac.STACValidationError as e:
        logging.warning(
            "Validation failed for DatasetDto %s converted to a STAC Collection %s: %s", dto.uuid, collection, e
        )
        raise

    return collection


# TESTING
if __name__ == "__main__":
    # TEST #1

    # UUID of a public dataset that we're using in testing:
    # https://app.hubocean.earth/catalog/dataset/wwf-oceansfutures-species
    dataset_uuid = "00acf0c5-d0ff-4f5e-a75c-ea691b9cc61b"

    client = OdpClient()
    dataset = client.catalog.get(dataset_uuid)

    print("\n--- Printing Test Dataset ---")
    # Expected:
    # {
    #     "spec": {
    #         "storage_class": "registry.hubocean.io/storageClass/tabular",
    #         "storage_controller": "registry.hubocean.io/storageController/storage-tabular",
    #         "data_collection": "catalog.hubocean.io/dataCollection/wwf-oceansfutures",
    #         "maintainer": {
    #             "contact": "Sarah Glaser <sarah.glaser@wwfus.org>",
    #             "organisation": "World Wildlife Fund US",
    #         },
    #         "citation": null,
    #         "documentation": ["https://www.oceansfutures.org/methodology"],
    #         "attributes": [],
    #         "facets": null,
    #         "tags": [
    #             "marine resources",
    #             "fish species",
    #             "Sea Around Us",
    #             "species distribution",
    #             "fisheries management",
    #             "species composition",
    #             "catch data",
    #             "commercial fishing",
    #             "EEZ",
    #             "SAU",
    #         ],
    #     },
    #     "kind": "catalog.hubocean.io/dataset",
    #     "version": "v1alpha3",
    #     "metadata": {
    #         "name": "wwf-oceansfutures-species",
    #         "display_name": "WWF Oceans Futures - Key Commercial Fish Species by EEZ",
    #         "description": "WWF Oceans Futures Phase 1 dataset detailing the top commercial fish species for each
    #         Exclusive Economic Zone (EEZ). Includes common species names and their relative importance as a percentage
    #         of the top 5 species caught in each EEZ, using Sea Around Us (SAU) EEZ identifiers.",
    #         "uuid": "00acf0c5-d0ff-4f5e-a75c-ea691b9cc61b",
    #         "labels": {
    #             "huboceanData": true,
    #             "raw_file_names": ["fish_species.csv"],
    #             "catalog.hubocean.io/released": true,
    #         },
    #         "owner": "16f81607-9bc0-455c-a77f-618ea68fa9a0",
    #     },
    #     "status": {
    #         "num_updates": 0,
    #         "created_time": "2024-12-20T12:12:11.653220",
    #         "created_by": "16f81607-9bc0-455c-a77f-618ea68fa9a0",
    #         "updated_time": "2024-12-20T12:12:11.653220",
    #         "updated_by": "16f81607-9bc0-455c-a77f-618ea68fa9a0",
    #         "deleted_time": null,
    #         "deleted_by": null,
    #     },
    # }
    print(dataset.json())

    # Convert DatasetDto to STAC Item
    # print(f"Converting DatasetDto {dataset_uuid} to a STAC Item")
    # stac_item = dto_to_stac(dataset_uuid, client)
    # print("Validating STAC Item")
    # stac_item.validate()

    # Print STAC Item
    # print("\n--- Printing STAC Item Spec ---")
    # print(json.dumps(stac_item.to_dict(), indent=4))

    # TEST #2

    # UUID of a public data collection that we're using in testing:
    # https://app.hubocean.earth/catalog/collection/moura2016-amazoncoral
    data_collection_uuid = "07c35450-3c95-4014-b65a-953269f69b77"

    data_collection = client.catalog.get(data_collection_uuid)

    print("\n--- Printing Test Data Collection ---")
    # Expected:
    # {
    #     "spec": {
    #         "distribution": {
    #             "published_by": {
    #                 "contact": "Thompson, Fabiano L. <fabianothompson1@gmail.com>",
    #                 "organisation": "Instituto de Biologia, Universidade Federal do Rio de Janeiro (UFRJ)",
    #             },
    #             "published_date": "2016-04-22T00:00:00",
    #             "website": "https://www.science.org/doi/full/10.1126/sciadv.1501252",
    #             "license": {
    #                 "name": "CC-BY-4.0",
    #                 "href": "https://creativecommons.org/licenses/by-nc/4.0/",
    #                 "full_text": null,
    #             },
    #         },
    #         "tags": [
    #             "Amazon River",
    #             "marine biology",
    #             "benthic habitats",
    #             "South Atlantic",
    #             "oceanography",
    #             "rhodoliths",
    #             "continental shelf",
    #             "mesophotic reefs",
    #             "reef system",
    #             "fisheries",
    #             "carbonate structures",
    #             "French Guiana",
    #             "ecosystem services",
    #             "climate change",
    #             "biogenic reefs",
    #             "Brazil",
    #             "sponge communities",
    #             "marine biodiversity",
    #             "river plume",
    #             "marine ecosystems",
    #         ],
    #         "facets": null,
    #     },
    #     "kind": "catalog.hubocean.io/dataCollection",
    #     "version": "v1alpha1",
    #     "metadata": {
    #         "name": "moura2016-amazoncoral",
    #         "display_name": "Amazon River Mouth Reef System (Moura et al. 2016)",
    #         "description": "Comprehensive dataset collection revealing an extensive and previously unknown reef system
    #         at the Amazon River mouth. The collection includes data from multidisciplinary surveys conducted between
    #         2010-2014 that discovered a significant carbonate system spanning approximately 9,500 km\u00b2 between
    #         French Guiana and Brazil. The datasets document reef structures, rhodolith beds, sponge communities, and
    #         fishing activities, along with oceanographic measurements and the seasonal influence of the Amazon River
    #         plume. This collection provides crucial baseline data about reef ecosystems functioning under marginal
    #         conditions, with implications for understanding reef systems' responses to climate change.",
    #         "uuid": "07c35450-3c95-4014-b65a-953269f69b77",
    #         "labels": {
    #             "etl_config": {
    #                 "type": "BlobStorage",
    #                 "azure_blob_container_name": "moura2016-amazoncoral",
    #                 "azure_blob_connection_string_secret_name": "sadatapipelines-connection-string",
    #             },
    #             "huboceanData": true,
    #             "catalog.hubocean.io/released": true,
    #         },
    #         "owner": "16f81607-9bc0-455c-a77f-618ea68fa9a0",
    #     },
    #     "status": {
    #         "num_updates": 1,
    #         "created_time": "2025-01-24T14:19:10.393967",
    #         "created_by": "16f81607-9bc0-455c-a77f-618ea68fa9a0",
    #         "updated_time": "2025-01-29T08:25:30.792966",
    #         "updated_by": "16f81607-9bc0-455c-a77f-618ea68fa9a0",
    #         "deleted_time": null,
    #         "deleted_by": null,
    #     },
    # }
    print(data_collection.json())

    # Convert DataCollectionDto to STAC Collection
    # print(f"Converting DataCollectionDto {data_collection_uuid} to a STAC Collection")
    # stac_collection = dto_to_stac(data_collection_uuid, odp_client=client)
    # print("Validating STAC Collection")
    # stac_collection.validate()

    # Print STAC Collection
    # print("\n--- Printing STAC Collection Spec ---")
    # print(json.dumps(stac_collection.to_dict(), indent=4))
