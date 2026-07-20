import os
import pandas as pd

from src.nlp.pros_cons_generator import generate_pros_cons


def test_generate_pros_cons_creates_expected_output(tmp_path):
    output_path = tmp_path / "pros_cons_generated.csv"

    result = generate_pros_cons(output_path=str(output_path))

    assert isinstance(result, pd.DataFrame)
    assert not result.empty
    assert set(result.columns) == {
        "company_id",
        "type",
        "rule_id",
        "text",
        "confidence_pct",
    }
    assert os.path.exists(output_path)

    assert result["confidence_pct"].gt(60).all()
    assert set(result["type"]).issubset({"pro", "con"})

    company_ids = result["company_id"].astype(str).tolist()
    assert len(company_ids) >= 2
