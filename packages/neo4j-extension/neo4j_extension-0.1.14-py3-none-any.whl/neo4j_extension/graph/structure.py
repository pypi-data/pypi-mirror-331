from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    Any,
    LiteralString,
    Mapping,
    Optional,
    Self,
    Union,
)

import neo4j
import neo4j.graph

from ..types._abc import Neo4jType
from ..types._utils import (
    PythonType,
    convert_neo4j_to_python,
    ensure_neo4j_type,
    ensure_python_type,
    get_neo4j_property_type_name,
)
from ..types.primitive import Neo4jList, Neo4jString
from ..typing import GraphSchema, Property
from ..utils import escape_identifier


class Entity(ABC):
    properties: dict[str, Neo4jType]
    globalId: Optional[str]

    def __init__(
        self,
        properties: Mapping[str, Union[Neo4jType, PythonType]],
        globalId: Optional[str] = None,
    ) -> None:
        self.globalId = globalId
        self.properties = {
            k: ensure_neo4j_type(v) for k, v in properties.items()
        }

    def __getitem__(self, key: str) -> PythonType:
        return ensure_python_type(self.properties[key])

    def __setitem__(
        self, key: str, value: Union[Neo4jType, PythonType]
    ) -> None:
        self.properties[key] = ensure_neo4j_type(value)

    def to_python_props(self) -> dict[str, PythonType]:
        """
        Convert properties to Python basic types(dict).
        """
        result: dict[str, PythonType] = {}
        for k, v in self.properties.items():
            result[k] = convert_neo4j_to_python(v)
        if self.globalId:
            result["globalId"] = self.globalId
        return result

    def to_cypher_props(self) -> LiteralString:
        pairs: list[LiteralString] = []
        for k, v in self.properties.items():
            # 리스트인 경우 property 저장 가능 여부 검사
            if isinstance(v, Neo4jList):
                if not v.is_storable_as_property():
                    raise ValueError(
                        f"Property '{k}' contains a non-storable ListValue."
                    )
            pairs.append(f"{escape_identifier(k)}: {v.to_cypher()}")
        if self.globalId:
            pairs.append(
                f"globalId: {Neo4jString(self.globalId).to_cypher()}"
            )
        if not pairs:
            return "{}"
        return "{ " + ", ".join(pairs) + " }"

    @abstractmethod
    def to_cypher(self) -> LiteralString: ...

    @classmethod
    @abstractmethod
    def from_neo4j(cls, entity: neo4j.graph.Entity) -> Self: ...

    @property
    def id(self) -> str:
        return f"{self.globalId or self.__class__.__name__ + '_' + str(id(self))}"

    def __repr__(self) -> LiteralString:
        return self.to_cypher()

    @abstractmethod
    def __str__(self) -> str: ...


class Node(Entity):
    labels: frozenset[str]

    def __init__(
        self,
        properties: Mapping[str, Union[Neo4jType, PythonType]],
        labels: Optional[set[str] | frozenset[str]] = None,
        globalId: Optional[str] = None,
    ) -> None:
        super().__init__(properties=properties, globalId=globalId)
        self.labels = frozenset(labels or ())

    @classmethod
    def from_neo4j(  # pyright: ignore[reportIncompatibleMethodOverride]
        cls,
        entity: neo4j.graph.Node,
    ) -> Self:
        properties: dict[str, Any] = entity._properties
        globalId = properties.get("globalId")
        if globalId:
            globalId = str(globalId)
        else:
            globalId = None
        return cls(
            properties=properties, labels=entity.labels, globalId=globalId
        )

    def __str__(self) -> str:
        return f"({self.labelstring}){self.to_python_props()}"

    def to_cypher(self) -> LiteralString:
        props: LiteralString = self.to_cypher_props()
        return f"({escape_identifier(self.id)}: {self.safe_labelstring} {props})"

    @property
    def labelstring(self) -> str:
        labels: str = ":".join(sorted(self.labels))
        return labels or "Node"

    @property
    def safe_labelstring(self) -> LiteralString:
        labels: LiteralString = ":".join(
            escape_identifier(label) for label in sorted(self.labels)
        )
        return labels or "Node"


class Relationship(Entity):
    rel_type: str
    start_node: Node
    end_node: Node

    def __init__(
        self,
        properties: Mapping[str, Union[Neo4jType, PythonType]],
        rel_type: str,
        start_node: Node,
        end_node: Node,
        globalId: Optional[str] = None,
    ) -> None:
        super().__init__(properties=properties, globalId=globalId)
        self.rel_type = rel_type
        self.start_node = start_node
        self.end_node = end_node

    def __str__(self) -> str:
        return f"[{self.start_node.id} {self.rel_type} {self.end_node.id}]{self.to_python_props()}"

    @classmethod
    def from_neo4j(  # pyright: ignore[reportIncompatibleMethodOverride]
        cls,
        entity: neo4j.graph.Relationship,
    ) -> Self:
        if entity.start_node is None or entity.end_node is None:
            raise ValueError(
                "Relationship must have both a start and end node."
            )
        properties: dict[str, Any] = entity._properties
        globalId = properties.get("globalId")
        if globalId:
            globalId = str(globalId)
        else:
            globalId = None
        return cls(
            properties=properties,
            rel_type=entity.type,
            start_node=Node.from_neo4j(entity.start_node),
            end_node=Node.from_neo4j(entity.end_node),
            globalId=globalId,
        )

    def to_cypher(self) -> LiteralString:
        start_node: LiteralString = self.start_node.to_cypher()
        id: LiteralString = escape_identifier(self.id)
        rel_type: LiteralString = escape_identifier(self.rel_type)
        props_str: LiteralString = self.to_cypher_props()
        end_node: LiteralString = self.end_node.to_cypher()
        return f"{start_node}-[{id}: {rel_type} {props_str}]->{end_node}"


class Graph:
    def __init__(
        self,
        nodes: Optional[dict[str, Node]] = None,
        relationships: Optional[dict[str, Relationship]] = None,
    ) -> None:
        self.nodes: dict[str, Node] = nodes or {}
        self.relationships: dict[str, Relationship] = relationships or {}

    def __repr__(self) -> str:
        if self.nodes:
            n = (
                "\n"
                + "\n".join("- " + str(n) for n in self.nodes.values())
                + "\n"
            )
        else:
            n = ""

        if self.relationships:
            r = (
                "\n"
                + "\n".join(
                    "- " + str(r) for r in self.relationships.values()
                )
                + "\n"
            )
        else:
            r = ""

        return f"### Nodes {n}\n### Relationships{r}"

    @classmethod
    def from_neo4j(cls, graph: neo4j.graph.Graph) -> Graph:
        result = cls()
        for entity in graph.nodes:
            result.add_node(Node.from_neo4j(entity))
        for entity in graph.relationships:
            result.add_relationship(Relationship.from_neo4j(entity))
        return result

    def add_node(self, node: Node) -> None:
        self.nodes[node.id] = node

    def add_relationship(self, relationship: Relationship) -> None:
        self.relationships[relationship.id] = relationship

    def remove_node(self, node_id: str) -> None:
        to_remove: list[str] = []
        for rid, rel in self.relationships.items():
            if rel.start_node.id == node_id or rel.end_node.id == node_id:
                to_remove.append(rid)
        for rid in to_remove:
            self.remove_relationship(rid)
        self.nodes.pop(node_id, None)

    def remove_relationship(self, rel_id: str) -> None:
        self.relationships.pop(rel_id, None)

    # ----------------------------------------------------------------------------
    # (1) Graph 객체 자체에서 스키마를 추출하는 메서드 추가
    # ----------------------------------------------------------------------------
    def get_graph_schema(self) -> GraphSchema:
        """
        현재 in-memory Graph에 존재하는 Node/Relationship 정보를 기반으로
        간단한 스키마 정보를 구성해 GraphSchema(dict) 형태로 반환한다.
        """

        # node_props_dict[label] = set of (propName, propType)
        node_props_dict: dict[str, set[tuple[str, str]]] = {}
        # rel_props_dict[rel_type] = set of (propName, propType)
        rel_props_dict: dict[str, set] = {}

        # relationships_list = list of { start: <label>, type: <rel_type>, end: <label> }
        relationships: set[tuple[str, str, str]] = set()

        # 1) 노드 정보 수집
        for node in self.nodes.values():
            # 여러 레이블을 콜론(:)으로 합쳐 하나의 문자열로 취급
            # 예: frozenset({'Person','Teacher'}) => "Person:Teacher"
            labels: str = node.labelstring
            node_props_dict.setdefault(labels, set())

            # 노드 타입별로 prop key / type
            for prop_key, neo4j_val in node.properties.items():
                prop_type_name: str = get_neo4j_property_type_name(neo4j_val)
                node_props_dict[labels].add((prop_key, prop_type_name))

        # 2) 관계 정보 수집
        for rel in self.relationships.values():
            rel_props_dict.setdefault(rel.rel_type, set())

            # 관계 타입별로 prop key / type
            for prop_key, neo4j_val in rel.properties.items():
                prop_type_name: str = get_neo4j_property_type_name(neo4j_val)
                rel_props_dict[rel.rel_type].add((prop_key, prop_type_name))

            relationships.add(
                (
                    rel.start_node.safe_labelstring,
                    rel.rel_type,
                    rel.end_node.safe_labelstring,
                )
            )

        # 3) Neo4jConnection의 query 결과 형태에 맞춰 변환
        node_props: dict[str, list[Property]] = {}
        for label, propset in node_props_dict.items():
            # [{ property: <str>, type: <str>}, ...] 형태로
            node_props[label] = [
                {"property": prop_name, "type": prop_type}
                for (prop_name, prop_type) in sorted(propset)
            ]

        rel_props: dict[str, list[Property]] = {}
        for rtype, propset in rel_props_dict.items():
            rel_props[rtype] = [
                {"property": prop_name, "type": prop_type}
                for (prop_name, prop_type) in sorted(propset)
            ]

        graph_schema: GraphSchema = {
            "node_props": node_props,
            "rel_props": rel_props,
            "relationships": [
                {
                    "start": start,
                    "type": rtype,
                    "end": end,
                }
                for (start, rtype, end) in sorted(relationships)
            ],
            "metadata": {
                "constraint": [],
                "index": [],
            },
        }
        return graph_schema

    # ----------------------------------------------------------------------------
    # (2) 포매팅된 스키마 문자열을 반환하는 메서드 추가
    # ----------------------------------------------------------------------------
    def get_formatted_graph_schema(self) -> str:
        """
        현재 그래프의 스키마 정보를 사람이 읽기 좋은 형식의 문자열로 반환한다.
        (Neo4jConnection.format_graph_schema()와 유사 형식)
        """
        schema = self.get_graph_schema()

        lines: list[str] = []
        lines.append("### Node properties")
        node_props = schema.get("node_props", {})

        for label, props in node_props.items():
            lines.append(f"- {label}")
            for p in props:
                lines.append(f"  * {p['property']}: {p['type']}")

        lines.append("")
        lines.append("### Relationship properties")
        rel_props = schema.get("rel_props", {})
        for rtype, rprops in rel_props.items():
            lines.append(f"- {rtype}")
            for rp in rprops:
                lines.append(f"  * {rp['property']}: {rp['type']}")

        lines.append("")
        lines.append("### Relationships")
        rels = schema.get("relationships", [])
        for rel_dict in rels:
            lines.append(
                f"- (:{rel_dict['start']})-[:{rel_dict['type']}]->(:{rel_dict['end']})"
            )

        return "\n".join(lines)

    def to_cypher(self) -> str:
        node_queries: list[str] = []
        for node in self.nodes.values():
            node_query = f"({escape_identifier(node.id)}:{node.safe_labelstring} {node.to_cypher_props()})"
            node_queries.append(node_query)
        rel_queries: list[str] = []
        for rel in self.relationships.values():
            rel_query = (
                f"({escape_identifier(rel.start_node.id)})-"
                f"[{escape_identifier(rel.id)}:{escape_identifier(rel.rel_type)} {rel.to_cypher_props()}]->"
                f"({escape_identifier(rel.end_node.id)})"
            )
            rel_queries.append(rel_query)
        all_queries = node_queries + rel_queries
        cypher = "CREATE\n  " + ",\n  ".join(all_queries) + ";"
        return cypher


if __name__ == "__main__":
    print(Node(properties={}).to_cypher())
    graph = Graph()
    node1 = Node({"name": "Alice"}, {"Person"}, "alice")
    node2 = Node({"name": "Bob"}, {"Person"}, "bob")
    rel = Relationship(
        {"since": 1999}, "KNOWS", node1, node2, "alice_knows_bob"
    )
    graph.add_node(node1)
    graph.add_node(node2)
    graph.add_relationship(rel)
    print(node1)
    print(node2)
    print(rel)
    print(graph.nodes)
    print(graph.relationships)
    graph.remove_node("alice")
    print(graph.nodes)
    print(graph.relationships)
    graph.remove_relationship("alice_knows_bob")
    print(graph.relationships)
