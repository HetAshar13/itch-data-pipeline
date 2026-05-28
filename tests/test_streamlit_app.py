from streamlit.testing.v1 import AppTest


def test_streamlit_app_renders_liquidityiq_demo_without_extraction():
    app = AppTest.from_file("app/streamlit_app.py")

    app.run(timeout=30)

    assert len(app.exception) == 0
    assert app.title[0].value == "LiquidityIQ"
    assert "Executive Overview" in [subheader.value for subheader in app.subheader]
    assert "Execution Cost Lab" in [subheader.value for subheader in app.subheader]
    assert "Evidence" in [subheader.value for subheader in app.subheader]
    assert "Data Mode" in [header.value for header in app.header]
