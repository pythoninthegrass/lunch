#!/usr/bin/env python3

import flet as ft
from flet import (
    Column,
    Container,
    ElevatedButton,
    RoundedRectangleBorder,
    Page,
    Row,
    Text,
)
import random
# import sqlite3
# from datetime import datetime
from util import *
from dataclasses import dataclass, field
from pathlib import Path
# from sqlmodel import Field, Session, SQLModel, create_engine, select
from typing import Optional, Dict, List, Tuple


@dataclass
class CustomButton():
    text: str
    style: Tuple = field(default_factory=lambda: ft.ButtonStyle(shape={
        ft.ControlState.DEFAULT: RoundedRectangleBorder(radius=2),
    }))
    on_click: Optional[ft.ElevatedButton().on_click] = None

    def __call__(self, text):
        return ft.ElevatedButton(
                text=self.text,
                style=self.style,
                on_click=self.on_click,
            )


class Lunch(ft.Column):
    def __init__(self, page: Page):
        super().__init__()
        self.page = page
        self.result = ft.Text("")
        self.expand = True

    def did_mount(self):
        self.build()

    def build(self):
        self.page.title = "Lunch"
        self.page.background_color = ft.Colors.WHITE
        self.page.padding = 10

        choice = ft.RadioGroup(
            content=ft.Row([
                ft.Container(ft.Radio(value="cheap", label="Cheap"), alignment=ft.Alignment(0.0, 0.0)),
                ft.Container(ft.Radio(value="normal", label="Normal"), alignment=ft.Alignment(0.0, 0.0)),
            ],
            alignment=ft.MainAxisAlignment.CENTER,)
        )

        row = Row(
            controls=[
                Container(CustomButton(text="Roll Lunch")(self.page), alignment=ft.Alignment(0.0, 0.0), on_click=self.button_clicked, data="roll"),
                Container(CustomButton(text="Delete Restaurant")(self.page), alignment=ft.Alignment(0.0, 0.0), on_click=self.button_clicked, data="delete"),
                Container(CustomButton(text="Add Restaurant")(self.page), alignment=ft.Alignment(0.0, 0.0), on_click=self.button_clicked, data="add"),
                Container(CustomButton(text="List All")(self.page), alignment=ft.Alignment(0.0, 0.0), on_click=self.button_clicked, data="list"),
            ],
            alignment=ft.MainAxisAlignment.CENTER,
        )

        self.controls.append(ft.Text("Click below to find out what's for Lunch:"))
        self.controls.append(choice)
        self.controls.append(row)
        self.controls.append(self.result)

    # TODO: connect to db; bind to buttons; create views based on button clicks
    def roll_lunch(self, option):
        restaurant = rng_restaurant(option)
        print(restaurant)

    def delete_restaurant(self):
        pass

    def add_restaurant(self):
        pass

    def list_all(self):
        pass

    # TODO: debug row + button click
    def button_clicked(self, e):
        data = e.control.data
        if self.result.value == "roll" or data == "roll":
            self.roll_lunch(data)
        elif data == "delete":
            self.delete_restaurant()
        elif data == "add":
            self.add_restaurant()
        elif data == "list":
            self.list_all()


def main(page: Page):
    page.title = "Lunch"
    page.window_width = 650
    page.window_height = 275
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    # create application instance
    lunch = Lunch(page)

    # add application's root control to page
    page.add(lunch)

    def bs_dismissed(e):
        print("Dismissed!")

    def show_bs(e):
        bs.open = True
        bs.update()

    def close_bs(e):
        bs.open = False
        bs.update()

    bs = ft.BottomSheet(
        ft.Container(
            ft.Column(
                [
                    ft.Text("This is sheet's content!"),
                    ft.ElevatedButton("Close bottom sheet", on_click=close_bs),
                ],
                tight=True,
            ),
            padding=10,
        ),
        open=True,
        on_dismiss=bs_dismissed,
    )
    page.overlay.append(bs)
    page.add(ft.ElevatedButton("Display bottom sheet", on_click=show_bs))

    Lunch.button_clicked = show_bs

ft.app(target=main)
