from .models import Item
from decimal import Decimal

def check_stock(name):
    """Look up how many of an item we have."""
    item = Item.objects.filter(name__iexact=name).first()
    if item is None:
        return {"error": f"No item named '{name}' exists in the inventory."}
    return {"name": item.name, "quantity": item.quantity, "price": float(item.price)}


def list_items():
    """Return every item in the inventory."""
    items = Item.objects.all()
    return {"items": [{"name": i.name, "quantity": i.quantity, "price": float(i.price)} for i in items]}


def add_item(name, quantity, price):
    """Create a new item, or add to an existing one's stock."""
    item = Item.objects.filter(name__iexact=name).first()
    if item is not None:
        item.quantity += quantity
        if price is not None:
            item.price = Decimal(str(price))
        item.save()
        return {"name": item.name, "quantity": item.quantity, "price": float(item.price), "created": False}
    item = Item.objects.create(name=name, quantity=quantity,price=Decimal(str(price)))
    return {"name": item.name, "quantity": item.quantity, "price": float(item.price), "created": True}


def remove_stock(name, quantity):
    """Take a quantity out of stock."""
    item = Item.objects.filter(name__iexact=name).first()
    if item is None:
        return {"error": f"No item named '{name}' exists in the inventory."}
    if quantity > item.quantity:
        return {
            "error": f"Cannot remove {quantity}. Only {item.quantity} in stock.",
            "name": item.name,
            "quantity": item.quantity,
        }
    item.quantity -= quantity
    item.save()
    return {"name": item.name, "quantity": item.quantity, "price": float(item.price),}


def delete_item(name):
    """Remove an item from the inventory entirely."""
    item = Item.objects.filter(name__iexact=name).first()
    if item is None:
        return {"error": f"No item named '{name}' exists in the inventory."}
    item.delete()
    return {"deleted": name}

def calculate_cost(name, quantity, vat_percent):
    """Calculate the cost of a given quantity of an item with VAT"""
    item = Item.objects.filter(name__iexact=name).first()
    if item is None:
        return {"error": f"No item named '{name}' exists in the inventory."}
    if quantity <=0:
        return{"error": "Quantity must be positive"}

    subtotal = item.price*Decimal(str(quantity))
    vat = subtotal*Decimal(str(vat_percent))/Decimal("100")

    total = subtotal + vat
    return {"name": item.name, "quantity": quantity,"unit_price": float(item.price), "subtotal": float(subtotal), "vat_percent": vat_percent, "vat_amount": float(vat), "total": float(total)}


TOOL_DECLARATIONS = [
    {
        "type": "function",
        "name": "check_stock",
        "description": "Look up the current quantity of a single item in the inventory. Use this whenever the user asks whether something is in stock or how many there are.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the item, e.g. 'Hammer'.",
                },
            },
            "required": ["name"],
        },
    },
    {
        "type": "function",
        "name": "list_items",
        "description": "Return every item in the inventory with its quantity. Use this when the user asks what is in stock generally, or asks for a list, rather than about one specific item.",
        "parameters": {"type": "object", "properties": {}},
    },
    {
        "type": "function",
        "name": "add_item",
        "description": "Add stock to the inventory. If the item does not exist it is created; if it already exists the quantity is added to the existing total. Use this for restocking and for new deliveries. A price can also be provided.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the item, e.g. 'Hammer'.",
                },
                "quantity": {
                    "type": "integer",
                    "description": "How many units to add. Must be positive.",
                },
                "price": {
                    "type": "number",
                    "description": "The price of one unit of the item.",
                },
            },
            "required": ["name", "quantity"],
        },
    },
    {
        "type": "function",
        "name": "remove_stock",
        "description": "Reduce the quantity of an existing item. Use this when items are sold, shipped or used. This does NOT delete the item; it only lowers the number.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the item, e.g. 'Hammer'.",
                },
                "quantity": {
                    "type": "integer",
                    "description": "How many units to remove. Must be positive.",
                },
            },
            "required": ["name", "quantity"],
        },
    },
    {
        "type": "function",
        "name": "delete_item",
        "description": "Permanently remove an item and its record from the inventory entirely. This is destructive. Only use it when the user clearly wants the item gone, not when they want to reduce its quantity.",
        "parameters": {
            "type": "object",
            "properties": {

                "name": {
                    "type": "string",
                    "description": "The name of the item to delete.",
                },
            },
            "required": ["name"],
        },   
    },
    {
        "type": "function",
        "name": "calculate_cost",
        "description": "Calculate the total cost of a specified quantity of an inventory item after adding the specified VAT percentage.",
        "parameters": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "The name of the item, e.g. 'Chocolate Bar'.",
                },
                "quantity": {
                    "type": "integer",
                    "description": "The number of items to calculate the cost for.",
                },
                "vat_percent": {
                    "type": "number",
                    "description": "The VAT percentage to add, for example 10 for 10% VAT.",
                },
            },
            "required": ["name", "quantity", "vat_percent"],
        },
    },
]

TOOL_FUNCTIONS = {
    "check_stock": check_stock,
    "list_items": list_items,
    "add_item": add_item,
    "remove_stock": remove_stock,
    "delete_item": delete_item,
    "calculate_cost": calculate_cost,
}
