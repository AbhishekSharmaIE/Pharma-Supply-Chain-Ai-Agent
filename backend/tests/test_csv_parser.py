from utils.csv_parser import parse_csv


def test_csv_parser_valid_rows():
    content = (
        "order_id,product_name,quantity,customer_tier,urgency_flag,stock_available,"
        "expiry_date,customer_location,warehouse_location,order_date\n"
        "ORD1,Drug A,10,gold,true,5,2026-05-01,Dublin,Dublin,2026-04-05\n"
        "ORD2,Drug B,20,standard,false,30,2026-08-01,Cork,Galway,2026-04-05\n"
    ).encode("utf-8")
    rows = parse_csv(content)
    assert len(rows) == 2


def test_csv_parser_skips_invalid_rows():
    content = (
        "order_id,product_name,quantity,customer_tier,urgency_flag,stock_available,"
        "expiry_date,customer_location,warehouse_location,order_date\n"
        "ORD1,Drug A,10,gold,true,5,2026-05-01,Dublin,Dublin,2026-04-05\n"
        "ORD2,Drug B,bad-int,standard,false,30,2026-08-01,Cork,Galway,2026-04-05\n"
    ).encode("utf-8")
    rows = parse_csv(content)
    assert len(rows) == 1
