from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from board import Board
import itertools
import flet as ft
from item import Item
from data_store import DataStore


class BoardList(ft.Container):
    id_counter = itertools.count()

    def __init__(
        self,
        board: "Board",
        store: DataStore,
        title: str,
        page: ft.Page,
        color: str = "",
    ):
        self.active_filter = None  # Cor da etiqueta selecionada para filtrar
        self.page: ft.Page = page
        self.board_list_id = next(BoardList.id_counter)
        self.store: DataStore = store
        self.board = board
        self.title = title
        self.color = color
        self.items = ft.Column([], tight=True, spacing=4)
        self.items.controls = self.store.get_items(self.board_list_id)
        self.new_item_field = ft.TextField(
            label="new card name",
            height=50,
            bgcolor=ft.Colors.WHITE,
            on_submit=self.add_item_handler,
        )

        self.end_indicator = ft.Container(
            bgcolor=ft.Colors.BLACK26,
            border_radius=ft.border_radius.all(30),
            height=3,
            width=200,
            opacity=0.0,
        )

        self.edit_field = ft.Row(
            [
                ft.TextField(
                    value=self.title,
                    width=150,
                    height=40,
                    content_padding=ft.padding.only(left=10, bottom=10),
                ),
                ft.TextButton(text="Save", on_click=self.save_title),
            ]
        )

        # Dropdown para filtrar por etiquetas
        self.filter_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option(
                    text=color,
                    key=hex_code,
                    content=ft.Row(
                        [
                            ft.Container(
                                width=15,
                                height=15,
                                bgcolor=hex_code,
                                border_radius=10
                            ),
                            ft.Text(color)
                        ],
                        spacing=5
                    )
                ) for color, hex_code in Item.LABEL_COLORS.items()
            ],
            hint_text="Filter by tag",
            width=120,
            on_change=self.filter_items
        )

        self.header = ft.Container(
            content=ft.Row(
                controls=[
                    ft.Text(
                        value=self.title,
                        size=16,
                        weight=ft.FontWeight.W_600,
                        color=ft.Colors.BLUE_GREY_900,
                        text_align=ft.TextAlign.LEFT,
                        overflow=ft.TextOverflow.ELLIPSIS,
                        expand=True,
                    ),
                    ft.PopupMenuButton(
                        icon=ft.Icons.MORE_HORIZ,
                        icon_color=ft.Colors.BLUE_GREY_400,
                        items=[
                            ft.PopupMenuItem(
                                icon=ft.Icons.EDIT,
                                text="Edit",
                                on_click=self.edit_title,
                            ),
                            ft.PopupMenuItem(icon=ft.Icons.DELETE, text="Delete", on_click=self.delete_list),
                            ft.PopupMenuItem(icon=ft.Icons.SWAP_HORIZ, text="Move List"),
                        ],
                    ),
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            padding=ft.padding.only(bottom=8),
        )

        self.inner_list = ft.Container(
            content=ft.Column(
                [
                    self.header,
                    self.filter_dropdown,
                    self.new_item_field,
                    ft.Container(
                        width=200,
                        content=ft.TextButton(
                            content=ft.Row(
                                [
                                    ft.Icon(ft.Icons.ADD, color=ft.Colors.BLUE, size=16),
                                    ft.Text("Add card", size=14, color=ft.Colors.BLUE, weight=ft.FontWeight.W_500),
                                ],
                                spacing=4,
                                alignment=ft.MainAxisAlignment.CENTER,
                            ),
                            style=ft.ButtonStyle(
                                overlay_color=ft.Colors.BLUE_50,
                                padding=ft.padding.all(6),
                            ),
                            on_click=self.add_item_handler,
                        ),
                        padding=ft.padding.only(top=6, bottom=6),
                    ),
                    ft.Container(
                        content=ft.Column(
                            [
                                self.items,
                                self.end_indicator,
                            ],
                            spacing=6,
                            scroll=ft.ScrollMode.AUTO,
                        ),
                        expand=True,
                    ),
                ],
                spacing=6,
                data=self.title,
                expand=True
            ),
            width=250,
            expand=True,
            border=ft.border.all(1, ft.Colors.BLACK26),
            border_radius=ft.border_radius.all(8),
            bgcolor=self.color if (self.color != "") else ft.Colors.WHITE,
            padding=ft.padding.all(10),
            shadow=ft.BoxShadow(
                spread_radius=1,
                blur_radius=3,
                color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
                offset=ft.Offset(0, 1),
            ),
        )

        self.view = ft.DragTarget(
            group="items",
            content=ft.Draggable(
                group="lists",
                content=ft.DragTarget(
                    group="lists",
                    content=self.inner_list,
                    data=self,
                    on_accept=self.list_drag_accept,
                    on_will_accept=self.list_will_drag_accept,
                    on_leave=self.list_drag_leave,
                ),
            ),
            data=self,
            on_accept=self.item_drag_accept,
            on_will_accept=self.item_will_drag_accept,
            on_leave=self.item_drag_leave,
        )
        super().__init__(content=self.view, data=self)

    def item_drag_accept(self, e):
        src = self.page.get_control(e.src_id)
        source_item = src.data
        
        # Create a new item with the same properties as the source item
        new_item = Item(self, self.store, source_item.item_text)
        new_item.labels = source_item.labels.copy()  # Copy labels
        new_item.priority = source_item.priority  # Copy priority
        new_item.deadline = source_item.deadline  # Copy deadline
        
        # Add the new item to this list
        control_to_add = ft.Column(
            [
                ft.Container(
                    bgcolor=ft.Colors.BLACK26,
                    border_radius=ft.border_radius.all(30),
                    height=3,
                    alignment=ft.alignment.center_right,
                    width=200,
                    opacity=0.0,
                )
            ]
        )
        control_to_add.controls.append(new_item)
        self.items.controls.append(control_to_add)
        self.store.add_item(self.board_list_id, new_item)
        
        # Remove the original item from its list
        source_item.list.remove_item(source_item)
        self.end_indicator.opacity = 0.0
        
        # First update the page to ensure all controls are properly added
        self.page.update()
        
        # Now it's safe to update the card appearance
        try:
            # Apply the labels and update display after the control is added to the page
            new_item.label_row.controls = [new_item.create_label_dot(color) for color in new_item.labels]
            
            # Update the card border based on priority
            priority_color = new_item.PRIORITY_COLORS.get(new_item.priority, "#000000")
            new_item.card_item.content.border = ft.border.all(2, priority_color)
            
            self.update()
        except Exception as e:
            print(f"Error updating card: {e}")
        

    def item_will_drag_accept(self, e):
        if e.data == "true":
            self.end_indicator.opacity = 1.0
        self.update()

    def item_drag_leave(self, e):
        self.end_indicator.opacity = 0.0
        self.update()

    def list_drag_accept(self, e):
        src = self.page.get_control(e.src_id)
        l = self.board.content.controls
        to_index = l.index(e.control.data)
        from_index = l.index(src.content.data)
        l[to_index], l[from_index] = l[from_index], l[to_index]
        self.inner_list.border = ft.border.all(2, ft.Colors.BLACK12)
        self.page.update()

    def list_will_drag_accept(self, e):
        if e.data == "true":
            self.inner_list.border = ft.border.all(2, ft.Colors.BLACK)
        self.update()

    def list_drag_leave(self, e):
        self.inner_list.border = ft.border.all(2, ft.Colors.BLACK12)
        self.update()

    def delete_list(self, e):
        self.board.remove_list(self, e)

    def edit_title(self, e):
        self.header.controls[0] = self.edit_field
        self.header.controls[1].visible = False
        self.update()

    def filter_items(self, e):
        """Filtra os itens baseado na etiqueta selecionada"""
        selected_color = self.filter_dropdown.value
        
        # Se a cor selecionada já está ativa, remove o filtro
        if selected_color == self.active_filter:
            self.active_filter = None
            self.filter_dropdown.value = None
        else:
            self.active_filter = selected_color

        # Atualiza a visibilidade dos itens
        for item_container in self.items.controls:
            item = item_container.controls[1]  # Acessa o Item dentro do Container
            if not self.active_filter or self.active_filter in item.labels:
                item_container.visible = True
            else:
                item_container.visible = False
        self.update()

    def save_title(self, e):
        self.title = self.edit_field.controls[0].value
        self.header.controls[0] = ft.Text(
            value=self.title,
            theme_style=ft.TextThemeStyle.TITLE_MEDIUM,
            text_align=ft.TextAlign.LEFT,
            overflow=ft.TextOverflow.CLIP,
            expand=True,
        )
        self.header.controls[1].visible = True
        self.update()

    def add_item_handler(self, e):
        if self.new_item_field.value == "":
            return
        self.add_item()

    def add_item(
        self,
        item: str | None = None,
        chosen_control: ft.Draggable | None = None,
        swap_control: ft.Draggable | None = None,
    ):
        try:
            controls_list = [x.controls[1] for x in self.items.controls]
            to_index = (
                controls_list.index(swap_control) if swap_control in controls_list else None
            )
            from_index = (
                controls_list.index(chosen_control)
                if chosen_control in controls_list
                else None
            )
            control_to_add = ft.Column(
                [
                    ft.Container(
                        bgcolor=ft.Colors.BLACK26,
                        border_radius=ft.border_radius.all(30),
                        height=3,
                        alignment=ft.alignment.center_right,
                        width=200,
                        opacity=0.0,
                    )
                ]
            )

            # rearrange (i.e. drag drop from same list)
            if (from_index is not None) and (to_index is not None):
                self.items.controls.insert(to_index, self.items.controls.pop(from_index))
                self.set_indicator_opacity(swap_control, 0.0)

            # insert (drag from other list to middle of this list)
            elif to_index is not None:
                new_item = Item(self, self.store, item)
                control_to_add.controls.append(new_item)
                self.items.controls.insert(to_index, control_to_add)
                self.store.add_item(self.board_list_id, new_item)

            # add new (drag from other list to end of this list, or use add item button)
            else:
                if not item and not self.new_item_field.value:
                    return
                    
                new_item = (
                    Item(self, self.store, item)
                    if item
                    else Item(self, self.store, self.new_item_field.value)
                )
                control_to_add.controls.append(new_item)
                self.items.controls.append(control_to_add)
                self.store.add_item(self.board_list_id, new_item)
                self.new_item_field.value = ""

            self.page.update()
        except Exception as e:
            print(f"Error adding item: {e}")
            return

    def remove_item(self, item: Item):
        controls_list = [x.controls[1] for x in self.items.controls]
        del self.items.controls[controls_list.index(item)]
        self.store.remove_item(self.board_list_id, item.item_id)
        self.view.update()

    def set_indicator_opacity(self, item, opacity):
        controls_list = [x.controls[1] for x in self.items.controls]
        self.items.controls[controls_list.index(item)].controls[0].opacity = opacity
        self.view.update()