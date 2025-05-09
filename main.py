#!/usr/bin/env python

import flet as ft                   # noqa: I001
from core.app import create_app


if __name__ == "__main__":
    ft.app(target=create_app)
