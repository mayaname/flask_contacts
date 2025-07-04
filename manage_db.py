"""
Program: App
Author: Maya Name
Creation Date: 06/03/2025
Revision Date: 
Description: The CLI application using the Rich module provides tools 
            to create, drop, and reset a SQL database. It also has an 
            option to populate the database from a CSV file. The user 
            can select options from a menu to perform these actions. 
            The application uses SQLAlchemy for database interactions 
            and Flask for the web framework.
             
Revisions:

"""


import csv
import os
import platform
import sys
from app import create_app
from app.extensions import db
from app.models import Employee
from sqlalchemy import inspect

from rich.console import Console
from rich.layout import Layout
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt, Confirm
from rich import box
from rich.align import Align

sys.tracebacklimit = 0  # Disable tracebacks

DISPLAY_WIDTH = 80
APP_TITLE = 'Manage Database'
OPT_1_TITLE = 'Create Database'
OPT_2_TITLE = 'Drop Database Tables'
OPT_3_TITLE = 'Populate Database'
OPT_4_TITLE = 'Reset Database'
OPT_5_TITLE = 'Exit Application'
MAIN_MENU_OPTIONS = 5

app = create_app()
console = Console(width=DISPLAY_WIDTH)

def validate_table_class(table_class: str) -> bool:
    """
        Description: Check if the entered table class 
                    name exists in the database.
        Param: table_class - Name of table in Flask model.py
        Return: T/F
    """
    with app.app_context():
        engine = db.engine
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        return table_class.lower() in table_names

def validate_field_names(table_class: str, field_names: list) -> bool:
    """
        Description: Check if the entered field names exist 
                    in the given table.
        Param: table_class - Name of table entered 
        Param: field_names - field names entered
        Return: T/F
    """
    with app.app_context():
        engine = db.engine
        inspector = inspect(engine)
        columns = inspector.get_columns(table_class.lower())
        actual_fields = {col['name'] for col in columns}
        return set(field_names).issubset(actual_fields)

def create_db(layout:Layout) -> None:
    """
        Description: Creates database and tables based om
                    Flask model.py
        Param: layout - layout for option panel
        Return: None
    """
    try:
        with app.app_context():
            db.create_all()
        display_message_panel(
            layout, 
            OPT_1_TITLE, 
            "[green]✅ Database created successfully.[/green]"
        )
    except Exception as e:
        db.session.rollback()
        display_message_panel(
            layout, 
            OPT_1_TITLE, 
            f"[bold red]Database error:[/bold red]\n[red]{e}[/red]"
        )

def drop_db(layout) -> None:
    """
        Description: Drops SQL database tables.
        Return: None
    """
    try:
        with app.app_context():
            db.drop_all()
        display_message_panel(
            layout, 
            OPT_2_TITLE, 
            "[yellow]⚠️  Database tables dropped.[/yellow]"
        )
    except Exception as e:
        db.session.rollback()
        display_message_panel(
            layout, 
            OPT_2_TITLE, 
            f"[bold red]Database error:[/bold red]\n[red]{e}[/red]"
        )

def populate_table(layout:Layout) -> None:
    """
        Description: Populate database from CSV
        Param: layout - layout for option panel
        Return: None
    """
    # First prompt: CSV filename
    csv_file = display_input_panel(
        layout, 
        OPT_3_TITLE, 
        "Enter CSV filename"
    )
    
    if not csv_file:
        return display_main_menu(layout)
    
    if not os.path.exists(csv_file):
        display_message_panel(
            layout, 
            OPT_3_TITLE, 
            f"[bold red]File not found:[/bold red] {csv_file}"
        )
        return display_main_menu(layout)

    # Second prompt: Table class name
    table_class = display_input_panel(
        layout, 
        OPT_3_TITLE, 
        "Enter table class name"
    )
    
    if not table_class:
        return display_main_menu(layout)
    
    if not validate_table_class(table_class):
        display_message_panel(
            layout, 
            OPT_3_TITLE, 
            f"[bold red]Table '{table_class}' not found in the database.[/bold red]"
        )
        return display_main_menu(layout)

    # Third prompt: Field names
    field_names = display_input_panel(
        layout, 
        OPT_3_TITLE, 
        "Enter table field names (space-separated)"
    )
    
    if not field_names:
        return display_main_menu(layout)
    
    field_names = field_names.strip().split()
    
    if not validate_field_names(table_class, field_names):
        with app.app_context():
            engine = db.engine
            inspector = inspect(engine)
            columns = inspector.get_columns(table_class.lower())
            actual_fields = {col['name'] for col in columns}
        
        display_message_panel(
            layout, 
            OPT_3_TITLE, 
            f"[bold red]Invalid field names for table '{table_class}'.[/bold red]\n"
            f"[bold yellow]Expected:[/bold yellow] {actual_fields}"
        )
        return display_main_menu(layout)

    # Perform database population
    with app.app_context():
        ModelClass = globals().get(table_class)
        if not ModelClass:
            display_message_panel(
                layout, 
                OPT_3_TITLE, 
                f"[bold red]Table class '[/bold red]{table_class}[bold red]' not found.[/bold red]"
            )
            return display_main_menu(layout)

        try:
            with open(csv_file, newline='', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        data = {field: row[field] for field in field_names}
                        record = ModelClass(**data)
                        db.session.add(record)
                    except Exception as e:
                        # Skip error rows but continue processing
                        continue
                db.session.commit()
            display_message_panel(
                layout,
                OPT_3_TITLE, 
                f"[green]✅ Table '[/green]{table_class}[green]' populated successfully.[/green]"
            )
        except Exception as e:
            db.session.rollback()
            display_message_panel(
                layout, 
                OPT_3_TITLE, 
                f"[bold red]An error occurred during population:[/bold red]\n[red]{e}[/red]"
            )

def reset_db(layout:Layout) -> None:
    """
        Description: Drops and recreates database tables.
        Param: layout - layout for option panel
        Return: None
    """
    try:
        with app.app_context():
            db.drop_all()
            db.create_all()
        display_message_panel(
            layout, 
            OPT_4_TITLE, 
            "[blue]🔄 Database reset successfully.[/blue]"
        )
    except Exception as e:
        db.session.rollback()
        display_message_panel(
            layout, 
            OPT_4_TITLE, 
            f"Database error:[/bold red]\n[red]{e}[/red]"
        )

def exit_app(layout:Layout) -> None:
    """
        Description: Exit confirmation prompt
        Param: layout - layout for option panel
        Return: None
    """
    if display_confirm_panel(
        layout, 
        OPT_5_TITLE, 
        "Exit program?"
    ):
        clear_display()
        console.print('\n[magenta]Application closed ...[/magenta]\n')
        sys.exit(0)
    else:
        display_main_menu(layout)

def clear_display() -> None:
    """
        Description: Clears Windows or Linux displays
        Return: None
    """
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def create_base_layout(title:str) -> Layout:
    """
        Description: Creates Rich base layout for app
        Param: title - Application title
        Return: layout - Base layout object
    """
    layout = Layout(name="root")
    layout.split(
        Layout(name="header", size=3),
        Layout(name="body", minimum_size=10),
        Layout(name="footer", size=3)
    )
    header_content = Text(title, justify="center", style="bold white on blue")
    layout["header"].update(Panel(header_content, style="blue", box=box.SQUARE))
    footer_text = Text(" ", justify="center", style="dim grey")
    layout["footer"].update(footer_text)
    return layout

def display_main_menu(layout:Layout = None) -> None:
    """
        Description: Displays app's main menu and 
                    prompts for option selection
        Param: layout - layout for menu panel (Default: None)
        Return: None
    """
    clear_display()
    if not layout:
        layout = create_base_layout(APP_TITLE)
    
    # Build menu options 
    menu_items = f"""
    1. {OPT_1_TITLE}
    2. {OPT_2_TITLE}
    3. {OPT_3_TITLE}
    4. {OPT_4_TITLE}
    5. {OPT_5_TITLE}
    """

    menu_content = Text("\n\n", justify="left")
    menu_content.append(Text(menu_items, style="green"))
    
    menu_panel = Panel(
        menu_content,
        title="[bold yellow]Main Menu[/bold yellow]",
        border_style="bright_green",
        padding=(1, 2),
        width=DISPLAY_WIDTH,  
        box=box.ROUNDED
    )
    
    # Center the panel in the body
    layout["body"].update(Align.center(menu_panel))
    console.print(layout)
    
    # Validate option selection
    menu_error_message = f'[bold red]Enter numeric value between 1 and {MAIN_MENU_OPTIONS}[/bold red]'
    while True:
        try:
            reply = Prompt.ask('\n[cyan]Enter menu option number[/cyan]', 
                              choices=[str(i) for i in range(1, MAIN_MENU_OPTIONS + 1)])
            reply = int(reply)
            if 1 <= reply <= MAIN_MENU_OPTIONS:
                break
            console.print(menu_error_message)
        except Exception:
            console.print(menu_error_message)

    # Reset layout for new view
    layout = create_base_layout(APP_TITLE)  

    match reply:
        case 1: create_db(layout)
        case 2: drop_db(layout)
        case 3: populate_table(layout)
        case 4: reset_db(layout)
        case 5: exit_app(layout)

def display_input_panel(layout:Layout, title:str, prompt:str) -> str:
    """
        Description: Display an option input panel for user input within 
                    the 'body'panel and return the value
        Param: layout - Input panel layout
        Param: title - Option title for input panel
        Param: prompt - Input prompt
        Return: Prompt string
    """
    clear_display()
    # Create centered content
    content = Align.center(Text(prompt, style="bold"))
    
    panel = Panel(
        content,
        title=f"[bold cyan]{title}[/bold cyan]",
        border_style="yellow",
        padding=(2, 4),
        width=DISPLAY_WIDTH,  
        box=box.ROUNDED
    )
    
    # Center the panel in the body
    layout["body"].update(Align.center(panel))
    console.print(layout)
    return input("> ").strip()

def display_message_panel(layout:Layout, title:str, message:str) -> None:
    """
        Description: Display an option message panel within the 'body'
                    panel and wait for user confirmation
        Param: layout - Message panel layout
        Param: title - Option title for message panel
        Param: message - Option message
        Return: None 
    """
    clear_display()
    content = Align.center(Text.from_markup(message))
    
    panel = Panel(
        content,
        title=f"[bold cyan]{title}[/bold cyan]",
        border_style="bright_blue",
        padding=(2, 4),
        width=DISPLAY_WIDTH,  
        box=box.ROUNDED
    )
    
    layout["body"].update(Align.center(panel))
    console.print(layout)
    # Pause to allow user to see results of option
    input("\nPress Enter to continue...")
    display_main_menu(layout)

def display_confirm_panel(layout:Layout, title:str, prompt:str) -> bool:
    """
        Description: Display a confirmation panel outside the 'body'
                    panel and return user choice
        Param: layout - Confirmation panel layout
        Param: title - Option title for confirmation panel
        Param: prompt - Confirmation with y/n prompt (Default: y)
        Return: T/F    
    
    """
    clear_display()
    content = Align.center(Text(prompt, style="bold yellow"))
    
    panel = Panel(
        content,
        title=f"[bold cyan]{title}[/bold cyan]",
        border_style="bright_red",
        padding=(2, 4),
        width=DISPLAY_WIDTH,  
        box=box.ROUNDED
    )
    
    layout["body"].update(Align.center(panel))
    console.print(layout)
    return Confirm.ask("[yellow]Confirm[/yellow]", default="y")

def main():
    while True:
        display_main_menu()

if __name__ == "__main__":
    main()