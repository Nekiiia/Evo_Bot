# handlers/order.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from database.db import get_cart, clear_cart
from products import products
from states import OrderForm
from config import config

order_router = Router()


@order_router.callback_query(F.data == "checkout")
async def start_order(callback: CallbackQuery, state: FSMContext):
    cart = await get_cart(callback.from_user.id)
    if not cart:
        await callback.answer("Корзина пуста!")
        return

    await state.set_state(OrderForm.name)
    await callback.message.edit_text("👤 Введите ваше имя:")


@order_router.message(OrderForm.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(OrderForm.contact)
    await message.answer("📞 Способ связи (Telegram username или телефон):")


@order_router.message(OrderForm.contact)
async def process_contact(message: Message, state: FSMContext):
    await state.update_data(contact=message.text)
    await state.set_state(OrderForm.address)
    await message.answer("⏰ Укажите удобное время для получения (или просто подтвердите):")


@order_router.message(OrderForm.address)
async def process_address(message: Message, state: FSMContext):
    data = await state.get_data()
    cart = await get_cart(message.from_user.id)

    order_text = f"""
🛍 <b>НОВЫЙ ЗАКАЗ — EVO Store</b>

👤 Имя: {data['name']}
📞 Связь: {data['contact']}
⏰ Время: {message.text}

🛒 Товары:
"""

    total = 0
    total_items = 0

    for item in cart:
        p = products[item["product_id"]]
        qty = item["quantity"]
        total_items += qty

        if item.get("price_type") == "debt":
            price = p["debt_price"]
            price_note = " (в долг)"
        else:
            price = p["price"]
            price_note = ""

        subtotal = price * qty
        order_text += f"{p['emoji']} {p['name']} × {qty} = {subtotal}€{price_note}\n"
        total += subtotal

    order_text += f"\n<b>Итого: {total}€</b>"

    if total_items >= 10:
        order_text += "\n\n🔥 ВНИМАНИЕ: Более 10 штук — возможна скидка!"

    order_text += "\n\nВыдача на вахте Evolution"

    # Отправляем админу
    await message.bot.send_message(
        config.ADMIN_ID, 
        order_text, 
        parse_mode="HTML"
    )

    await message.answer("✅ Заказ успешно оформлен!\nМы скоро свяжемся с вами.")
    
    await clear_cart(message.from_user.id)
    await state.clear()