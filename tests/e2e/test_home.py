
import re
import requests
from playwright.sync_api import Page, expect


BASE_URL = "http://127.0.0.1:5000/"


def test_user_login(page):
    page.goto(BASE_URL)
    page.locator("a:has-text('Connexion')").click()
    expect(page).to_have_title('Login | ENSET Douala')


