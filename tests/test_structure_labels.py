from docintelligence.core.models import AtomType, BBox, EvidenceAtom
from docintelligence.normalization.structure import infer_structure


def test_structure_inference_labels_common_patterns() -> None:
    heading = infer_structure(
        EvidenceAtom(
            atom_id="a1",
            doc_id="doc",
            page=1,
            atom_type=AtomType.TEXT,
            text="TABLE OF CONTENTS",
            bbox=BBox(x0=0, y0=0, x1=1, y1=1),
            parser_source="test",
        )
    )
    footnote = infer_structure(
        EvidenceAtom(
            atom_id="a2",
            doc_id="doc",
            page=1,
            atom_type=AtomType.TEXT,
            text="1 This is a longer note explaining the citation context in detail.",
            bbox=BBox(x0=0, y0=0, x1=1, y1=1),
            parser_source="test",
        )
    )
    caption = infer_structure(
        EvidenceAtom(
            atom_id="a3",
            doc_id="doc",
            page=1,
            atom_type=AtomType.TEXT,
            text="Figure 2 Results by Region",
            bbox=BBox(x0=0, y0=0, x1=1, y1=1),
            parser_source="test",
        )
    )

    assert heading.role_label == "table_of_contents"
    assert footnote.atom_type == AtomType.FOOTNOTE
    assert caption.atom_type == AtomType.CAPTION
