# handlers/user.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from keyboards.inline import main_menu, catalog_keyboard, cart_keyboard
from database.db import add_to_cart, get_cart, remove_from_cart, clear_cart
from products import products

user_router = Router()


@user_router.message(F.text == "/start")
async def cmd_start(message: Message):
    text = """
🌌 <b>Добро пожаловать в EVO Store</b>

🍉🍈🍒 Воздух для своих

<b>Цены:</b>
Основная цена: 
Электронка 40к - 15€
Электронка 50к - 17€
Жидкость 30ml - 10€

В долг/До аванса
Электронка 40к - 20€
Электронка 50к - 22€
Жидкость 30ml - 12€

При заказе от 10 шт. действуют скидки!🔥

Приём заказов <b>24/7</b>
Выдача: ежедневно с <b>14:00 до 02:00</b> в Evolution

Выбери нужный прайс ниже 👇
    """
    await message.answer(text, parse_mode="HTML", reply_markup=main_menu())

@user_router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery):
    await callback.message.edit_text(
        "🌌 <b>EVO Store</b>\nВыбери нужный прайс:",
        parse_mode="HTML",
        reply_markup=main_menu()
    )


@user_router.callback_query(F.data == "catalog_normal")
async def show_normal_catalog(callback: CallbackQuery):
    await callback.message.edit_text(
        "<b>🛍 Обычные цены</b>\n\nНажимай на товар, чтобы добавить:",
        parse_mode="HTML",
        reply_markup=catalog_keyboard(is_debt=False)
    )


@user_router.callback_query(F.data == "catalog_debt")
async def show_debt_catalog(callback: CallbackQuery):
    await callback.message.edit_text(
        "<b>💳 Цены в долг (до аванса)</b>\n\nНажимай на товар, чтобы добавить:",
        parse_mode="HTML",
        reply_markup=catalog_keyboard(is_debt=True)
    )

@user_router.callback_query(F.data.startswith("add_") & ~F.data.startswith("add_debt_"))
async def add_normal(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    await add_to_cart(callback.from_user.id, product_id, is_debt=False)
    await callback.answer("✅ Добавлено по обычной цене")


@user_router.callback_query(F.data.startswith("add_debt_"))
async def add_debt(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[2])
    await add_to_cart(callback.from_user.id, product_id, is_debt=True)
    await callback.answer("✅ Добавлено по цене в долг")


@user_router.callback_query(F.data.startswith("remove_"))
async def remove_from_cart_handler(callback: CallbackQuery):
    product_id = int(callback.data.split("_")[1])
    await remove_from_cart(callback.from_user.id, product_id)
    await callback.answer("🗑 Товар удалён")
    
    # Обновляем сообщение с корзиной
    cart = await get_cart(callback.from_user.id)
    if not cart:
        await callback.message.edit_text("🫙 Корзина пуста", reply_markup=main_menu())
        return
    
    text = "<b>🛒 Ваша корзина:</b>\n\n"
    total = 0
    for item in cart:
        p = products[item["product_id"]]
        subtotal = p["price"] * item["quantity"]
        text += f"{p['emoji']} {p['name']} × {item['quantity']} = {subtotal}€\n"
        total += subtotal
    text += f"\n<b>Итого: {total}€</b>"

    await callback.message.edit_text(
        text, 
        parse_mode="HTML", 
        reply_markup=cart_keyboard(cart)
    )


@user_router.callback_query(F.data == "clear_cart")
async def clear_cart_handler(callback: CallbackQuery):
    await clear_cart(callback.from_user.id)
    await callback.answer("🗑 Корзина полностью очищена")
    await callback.message.edit_text("🫙 Корзина пуста", reply_markup=main_menu())


@user_router.callback_query(F.data == "cart")
async def show_cart(callback: CallbackQuery):
    cart = await get_cart(callback.from_user.id)
    if not cart:
        await callback.message.edit_text("🫙 Корзина пуста", reply_markup=main_menu())
        return

    text = "<b>🛒 Ваша корзина:</b>\n\n"
    total = 0
    total_items = 0

    for item in cart:
        p = products[item["product_id"]]
        qty = item["quantity"]
        total_items += qty
        
        if item.get("price_type") == "debt":
            price = p["debt_price"]
            price_note = " <i>(в долг/до аванса)</i>"
        else:
            price = p["price"]
            price_note = ""

        subtotal = price * qty
        text += f"{p['emoji']} {p['name']} × {qty} = <b>{subtotal}€</b>{price_note}\n"
        total += subtotal

    text += f"\n<b>Итого: {total}€</b>"

    # Скидка при 10+ штук
    if total_items >= 10:
        text += "\n\n🔥 <b>10+ товаров в корзине!</b>\nНапишите админу для специальной цены"

    await callback.message.edit_text(
        text, 
        parse_mode="HTML", 
        reply_markup=cart_keyboard(cart)
    )