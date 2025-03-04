from vrs_anvil import generate_gnomad_ids


def test_generate_gnomad_ids(caching_translator):
    input_vcf = "tests/fixtures/test_vcf_input.vcf"
    errors = []
    results = []
    with open(input_vcf, "r") as f:
        for line in f:
            if line.startswith("#"):
                continue
            for gnomad_id in generate_gnomad_ids(line):
                try:
                    result = caching_translator.translate_from(
                        fmt="gnomad", var=gnomad_id
                    )
                    results.append((gnomad_id, result))
                except Exception as e:
                    errors.append((gnomad_id, e))
    print(errors)
    assert len(results) >= 12, f"Errors: {len(errors)} Successes: {len(results)}"
