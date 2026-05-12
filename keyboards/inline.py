
from aiogram.utils.keyboard import InlineKeyboardBuilder
from products import products


def main_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text="🛍 Основные цены", callback_data="catalog_normal")
    builder.button(text="💳 Цены в долг", callback_data="catalog_debt")
    builder.button(text="🛒 Корзина", callback_data="cart")
    builder.button(text="✍️ Написать админу", url="https://t.me/Evolution_Lv")  #
    builder.adjust(1)
    return builder.as_markup()


def catalog_keyboard(is_debt: bool = False):
    builder = InlineKeyboardBuilder()
    for pid, p in products.items():
        if is_debt:
            price_text = f"{p['emoji']} {p['name']} — {p['debt_price']}€"
            callback = f"add_debt_{pid}"
        else:
            price_text = f"{p['emoji']} {p['name']} — {p['price']}€"
            callback = f"add_{pid}"
        
        builder.button(text=price_text, callback_data=callback)
    
    builder.button(text="⬅️ В главное меню", callback_data="main_menu")
    builder.adjust(1)
    return builder.as_markup()


def cart_keyboard(cart_items):
    builder = InlineKeyboardBuilder()
    for item in cart_items:
        pid = item["product_id"]
        p = products[pid]
        builder.button(
            text=f"❌ {p['emoji']} {p['name']}",
            callback_data=f"remove_{pid}"
        )
    builder.button(text="➕ Продолжить покупки", callback_data="catalog_normal")
    builder.button(text="🗑 Очистить корзину", callback_data="clear_cart")
    builder.button(text="✅ Оформить заказ", callback_data="checkout")
    builder.adjust(1)
    return builder.as_markup()