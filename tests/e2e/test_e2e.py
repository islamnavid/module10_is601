
import pytest
from playwright.sync_api import expect


@pytest.mark.e2e
def test_hello_world(page, fastapi_server):
    """Test that the homepage displays Hello World."""
    page.goto("http://localhost:8000")

    expect(page.locator("h1")).to_have_text("Hello World")


@pytest.mark.e2e
def test_calculator_add(page, fastapi_server):
    """Test addition using the calculator interface."""
    page.goto("http://localhost:8000")

    page.fill("#a", "10")
    page.fill("#b", "5")

    page.get_by_role("button", name="Add", exact=True).click()

    expect(page.locator("#result")).to_have_text(
        "Result: 15",
        timeout=10000
    )


@pytest.mark.e2e
def test_calculator_divide_by_zero(page, fastapi_server):
    """Test division by zero error handling."""
    page.goto("http://localhost:8000")

    page.fill("#a", "10")
    page.fill("#b", "0")

    page.get_by_role("button", name="Divide", exact=True).click()

    expect(page.locator("#result")).to_have_text(
        "Error: Cannot divide by zero!",
        timeout=10000
    )
