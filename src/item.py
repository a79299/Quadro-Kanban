import flet as ft
import itertools
from data_store import DataStore
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from board_list import BoardList


class Item(ft.Container):
    id_counter = itertools.count()

    # Cores disponíveis para etiquetas (nome + cor hexadecimal)
    LABEL_COLORS = {
        "Vermelho": "#FF5733",
        "Verde": "#33FF57",
        "Azul": "#3357FF",
        "Amarelo": "#FFD700",
        "Roxo": "#800080",
    }

    # Prioridades disponíveis e suas cores de borda
    PRIORITY_COLORS = {
        "Alta": "#FF0000",    # Vermelho
        "Média": "#FFA500",   # Laranja
        "Baixa": "#008000"    # Verde
    }

    def __init__(self, list: "BoardList", store: DataStore, item_text: str):
        self.item_id = next(Item.id_counter)
        self.store: DataStore = store
        self.list = list
        self.page = list.page  # Inicializa o atributo page a partir da lista
        self.item_text = item_text
        self.labels = []  # Lista de cores das etiquetas
        self.priority = "Baixa"  # Prioridade padrão
        self.deadline = None  # Data limite (opcional)
        self.label_row = ft.Row(
            [self.create_label_dot(color) for color in self.labels],
            spacing=5,
            wrap=True,
        )

        # Dropdown para escolher a cor da etiqueta
        self.color_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option(
                    text=color,
                    key=hex_code,
                    content=ft.Row(
                        [
                            ft.Container(
                                width=12,
                                height=12,
                                bgcolor=hex_code,
                                border_radius=8
                            ),
                            ft.Text(color, size=12)
                        ],
                        spacing=4
                    )
                ) for color, hex_code in self.LABEL_COLORS.items()
            ],
            hint_text="Tag",
            width=90,
            text_size=12
        )

        # Dropdown para escolher a prioridade
        self.priority_dropdown = ft.Dropdown(
            options=[
                ft.dropdown.Option(
                    text=priority,
                    key=color,
                    content=ft.Row(
                        [
                            ft.Container(
                                width=12,
                                height=12,
                                bgcolor=color,
                                border_radius=8
                            ),
                            ft.Text(priority, size=12)
                        ],
                        spacing=4
                    )
                ) for priority, color in self.PRIORITY_COLORS.items()
            ],
            value="Baixa",
            hint_text="Prioridade",
            on_change=self.change_priority,
            width=90,
            text_size=12
        )

        # Campo para definir deadline
        self.deadline_picker = ft.TextField(
            label="Deadline",
            width=90,
            text_size=12,
            on_submit=self.set_deadline,
        )

        # Botão para adicionar etiqueta
        self.add_label_button = ft.IconButton(
            icon=ft.Icons.ADD,
            on_click=self.add_label,
        )

        # Botão para editar o item
        self.edit_button = ft.IconButton(
            icon=ft.Icons.EDIT,
            on_click=self.edit_item,
            icon_size=20,
            tooltip="Edit",
        )

        # Botão para eliminar o item
        self.delete_button = ft.IconButton(
            icon=ft.Icons.DELETE,
            on_click=self.delete_item,
            icon_size=20,
            tooltip="Delete",
        )

        # Exibição do cartão
        self.card_item = ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        # Área das etiquetas coloridas no canto superior esquerdo
                        self.label_row,
                        ft.Container(
                            content=ft.Text(
                                self.item_text,
                                size=12,
                                weight=ft.FontWeight.W_500,
                                overflow=ft.TextOverflow.ELLIPSIS,
                                max_lines=3,
                                text_align=ft.TextAlign.LEFT
                            ),
                            padding=ft.padding.only(top=6, bottom=6),
                            width=180
                        ),
                        ft.Container(
                            content=ft.Row([self.color_dropdown, self.add_label_button],
                                          spacing=2),
                            padding=ft.padding.only(top=2, bottom=2)
                        ),
                        ft.Container(
                            content=ft.Row([self.priority_dropdown, self.deadline_picker],
                                          spacing=2),
                            padding=ft.padding.only(top=2, bottom=2)
                        ),
                        ft.Container(
                            content=ft.Row(
                                [self.edit_button, self.delete_button],
                                alignment=ft.MainAxisAlignment.END,
                                spacing=0
                            ),
                            padding=ft.padding.only(top=2)
                        )
                    ],
                    spacing=0,
                    width=200,
                ),
                padding=ft.padding.all(6),
                bgcolor=ft.Colors.WHITE,
                border=ft.border.all(2, self.PRIORITY_COLORS[self.priority]),
                shadow=ft.BoxShadow(
                    spread_radius=1,
                    blur_radius=3,
                    color=ft.Colors.with_opacity(0.2, ft.Colors.BLACK),
                    offset=ft.Offset(0, 1)
                )
            ),
            elevation=2,
            surface_tint_color=ft.Colors.BLUE_GREY_100,
            data=self.list
        )

        self.view = ft.Draggable(
            group="items",
            content=ft.DragTarget(
                group="items",
                content=self.card_item,
                on_accept=self.drag_accept,
                on_leave=self.drag_leave,
                on_will_accept=self.drag_will_accept,
            ),
            data=self,
        )
        super().__init__(content=self.view)

    def create_label_dot(self, color: str):
        """Cria um pequeno círculo colorido para representar uma etiqueta"""
        return ft.Container(
            width=40,
            height=8,
            bgcolor=color,
            border_radius=4,
            opacity=0.8
        )

    def add_label(self, e):
        """Adiciona uma etiqueta com a cor escolhida pelo usuário"""
        selected_color = self.color_dropdown.value
        if selected_color and selected_color not in self.labels:
            self.labels.append(selected_color)
            self.update_card_labels()

    def update_card_labels(self):
        """Atualiza a exibição das etiquetas coloridas no cartão"""
        self.label_row.controls = [self.create_label_dot(color) for color in self.labels]
        self.page.update()

    def edit_item(self, e):
        """Abre um diálogo para editar o texto do item."""
        def close_dlg(e):
            if dialog_text.value != "":
                self.item_text = dialog_text.value
                self.update_card_display()  # Atualiza o texto no cartão
            self.page.close(dialog)

        dialog_text = ft.TextField(value=self.item_text, label="Edit item text")
        dialog = ft.AlertDialog(
            title=ft.Text("Edit Item"),
            content=dialog_text,
            actions=[
                ft.ElevatedButton(text="Save", on_click=close_dlg),
                ft.ElevatedButton(text="Cancel", on_click=lambda e: self.page.close(dialog)),
            ],
        )
        self.page.open(dialog)
        dialog_text.focus()

    def delete_item(self, e):
        """Exibe um diálogo de confirmação antes de eliminar o item."""

        def confirm_delete(e):  # Remove 'self' from parameters
            self.page.close(dialog)
            self.list.remove_item(self)  # Actually remove the item from the list

        dialog = ft.AlertDialog(
            title=ft.Text("Confirm Delete"),
            content=ft.Text("Are you sure you want to delete this item?"),
            actions=[
                ft.ElevatedButton(text="Delete", on_click=confirm_delete),
                ft.ElevatedButton(text="Cancel", on_click=lambda e: self.page.close(dialog)),
            ],
        )
        self.page.open(dialog)
    def update_card_display(self):
        """Atualiza o texto e aparência do cartão."""
        # Atualiza o texto do cartão
        for control in self.card_item.content.content.controls:
            if isinstance(control, ft.Container) and isinstance(control.content, ft.Text):
                control.content.value = self.item_text
                control.content.update()
                break

        # Atualiza a borda baseada na prioridade
        priority_color = self.PRIORITY_COLORS.get(self.priority, "#000000")
        self.card_item.border = ft.border.all(2, priority_color)

        # Atualiza a cor de fundo baseada no deadline
        if self.deadline:
            from datetime import datetime, timedelta
            try:
                deadline_date = datetime.strptime(self.deadline, "%d/%m/%Y")
                days_remaining = (deadline_date - datetime.now()).days
                
                if days_remaining < 0:
                    # Prazo expirado - vermelho claro
                    self.card_item.content.bgcolor = "#ffcccc"
                elif days_remaining <= 2:
                    # Próximo do prazo - amarelo claro
                    self.card_item.content.bgcolor = "#fff3cd"
                elif days_remaining <= 5:
                    # Aproximando do prazo - verde muito claro
                    self.card_item.content.bgcolor = "#d4edda"
                else:
                    # Prazo confortável - branco
                    self.card_item.content.bgcolor = ft.Colors.WHITE  # Update from colors to Colors
            except ValueError:
                # Em caso de erro no formato da data
                self.card_item.content.bgcolor = ft.colors.WHITE
        else:
            self.card_item.content.bgcolor = ft.colors.WHITE

        self.card_item.update()
        self.page.update()

    def change_priority(self, e):
        """Altera a prioridade do card e atualiza sua aparência"""
        self.priority = self.priority_dropdown.value
        self.update_card_display()

    def set_deadline(self, e):
        """Define ou atualiza o deadline do card"""
        from datetime import datetime
        try:
            # Tenta converter a string em data
            deadline_str = self.deadline_picker.value
            datetime.strptime(deadline_str, "%d/%m/%Y")
            self.deadline = deadline_str
            self.update_card_display()
        except ValueError:
            # Mostra erro se o formato da data for inválido
            dialog = ft.AlertDialog(
                title=ft.Text("Erro no formato da data"),
                content=ft.Text("Por favor, use o formato DD/MM/YYYY"),
                actions=[
                    ft.TextButton("OK", on_click=lambda e: self.page.close(dialog))
                ]
            )
            self.page.open(dialog)
    def drag_accept(self, e):
        src = self.page.get_control(e.src_id)
        source_item = src.data

        # Skip if item is dropped on itself
        if src.content.content == e.control.content:
            self.card_item.elevation = 1
            self.list.set_indicator_opacity(self, 0.0)
            e.control.update()
            return

        # Item dropped within same list but not on itself
        if source_item.list == self.list:
            self.list.add_item(chosen_control=source_item, swap_control=self)
            self.card_item.elevation = 1
            e.control.update()
            return

        # Mudando o item para outra lista
        old_list = source_item.list
        source_item.list = self.list
        
        # Adicionamos o item na nova posição
        self.list.add_item(chosen_control=source_item, swap_control=self)
        
        # Removemos da lista antiga
        old_list.remove_item(source_item)
        
        self.list.set_indicator_opacity(self, 0.0)
        self.card_item.elevation = 1
        self.page.update()

    def drag_will_accept(self, e):
        if e.data == "true":
            self.list.set_indicator_opacity(self, 1.0)
        self.card_item.elevation = 20 if e.data == "true" else 1
        self.page.update()

    def drag_leave(self, e):
        self.list.set_indicator_opacity(self, 0.0)
        self.card_item.elevation = 1
        self.page.update()
