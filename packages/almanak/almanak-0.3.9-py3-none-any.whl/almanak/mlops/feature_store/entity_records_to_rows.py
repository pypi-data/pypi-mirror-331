from typing import List, Dict, Any


def entity_records_to_entity_rows(
    entity_records: Dict[str, Any],
) -> List[Dict[str, Any]]:
    return [
        {attribute: value}
        for attribute, collection in entity_records.items()
        for value in collection
    ]
