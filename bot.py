import asyncio
import json
import os
import uuid
import logging
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from config import (
    BOT_TOKEN, ADMIN_ID, SHOP_NAME,
    OPERATOR_LINK, REVIEWS_BOT_LINK,
    EXCHANGE_RATES, WALLETS, STATES, WEAPONS, CATEGORIES,
    SHIPPING_COSTS, SHIPPING_DAYS, SWITCH_SHIPPING, SWITCH_SHIPPING_DAYS
)

logging.basicConfig(level=logging.INFO)
os.makedirs("images", exist_ok=True)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

USERS_FILE = "users.json"
STOCK_FILE = "stock_status.json"
REQUESTS_FILE = "requests.json"

COINS = {
    "btc": {"name": "Bitcoin (BTC)", "symbol": "₿", "wallet": "btc", "rate": "USD_TO_BTC", "dec": 8},
    "ltc": {"name": "Litecoin (LTC)", "symbol": "Ł", "wallet": "ltc", "rate": "USD_TO_LTC", "dec": 6},
    "usdt": {"name": "USDT (TRC-20)", "symbol": "₮", "wallet": "usdt_trc20", "rate": "USD_TO_USDT", "dec": 2},
}


def load_json(path, default=None):
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {} if default is None else default


def save_json(path, data):
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def load_users():
    return load_json(USERS_FILE)


def save_users(u):
    save_json(USERS_FILE, u)


def load_requests():
    return load_json(REQUESTS_FILE)


def save_requests(r):
    save_json(REQUESTS_FILE, r)


def is_registered(uid):
    return str(uid) in load_users()


def register_user(uid, username, state):
    users = load_users()
    users[str(uid)] = {
        "username": username,
        "state": state,
        "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "orders_count": 0,
        "balance": 0,
        "total_deposited": 0,
    }
    save_users(users)


def get_user_state(uid):
    u = load_users().get(str(uid))
    return u.get("state") if u else None


def find_state_in_list(text):
    n = text.strip().lower()
    for key, data in STATES.items():
        if key == n or data["name"].lower() == n:
            return key
    return None


def get_state_key_by_name(name):
    if not name:
        return None
    n = name.strip().lower()
    for key, data in STATES.items():
        if data["name"].lower() == n:
            return key
    return None


def calculate_price(base, state_key, fixed=False):
    if fixed:
        return base
    price = int(base * STATES[state_key]["coefficient"])
    last = int(str(price)[-1])
    return price if last == 9 else price - last - 1


def get_shipping_cost(code, state_key):
    if code == "glock_switch":
        return SWITCH_SHIPPING
    return SHIPPING_COSTS.get(state_key, 50)


def get_shipping_days(state_key, code=""):
    if code == "glock_switch":
        return SWITCH_SHIPPING_DAYS
    return SHIPPING_DAYS.get(state_key, "3-5")


def is_in_stock(code):
    return load_json(STOCK_FILE).get(code, True)


def coin_amount(coin, usd):
    c = COINS[coin]
    return usd * EXCHANGE_RATES[c["rate"]]


def coin_str(coin, usd):
    c = COINS[coin]
    return f"{coin_amount(coin, usd):.{c['dec']}f} {coin.upper()}"


def new_request(data):
    rid = uuid.uuid4().hex[:12]
    reqs = load_requests()
    data["status"] = "pending"
    data["created_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reqs[rid] = data
    save_requests(reqs)
    return rid


def admin_kb(rid):
    return types.InlineKeyboardMarkup(inline_keyboard=[[
        types.InlineKeyboardButton(text="✅ Confirm", callback_data=f"admok_{rid}"),
        types.InlineKeyboardButton(text="❌ Decline", callback_data=f"admno_{rid}")
    ]])


def back_kb(target="back_to_profile", text="◀️ Back to Profile"):
    return types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text=text, callback_data=target)]
    ])


class RegistrationState(StatesGroup):
    entering_state = State()


class ProfileState(StatesGroup):
    changing_state = State()


class DepositState(StatesGroup):
    waiting_amount = State()


def get_main_keyboard():
    return types.ReplyKeyboardMarkup(keyboard=[
        [types.KeyboardButton(text="👤 Profile"), types.KeyboardButton(text="🔫 Catalog")],
        [types.KeyboardButton(text="📦 Purchases"), types.KeyboardButton(text="🆘 Support")],
        [types.KeyboardButton(text="⭐ Reviews")]
    ], resize_keyboard=True)


def get_catalog_keyboard():
    return types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Handguns", callback_data="cat_handguns")],
        [types.InlineKeyboardButton(text="Long Guns", callback_data="cat_long_guns")],
        [types.InlineKeyboardButton(text="SMG", callback_data="cat_smg")],
        [types.InlineKeyboardButton(text="Glock Switch", callback_data="weapon_glock_switch")]
    ])


def build_profile(uid):
    u = load_users()[str(uid)]
    text = (
        f"👤 PROFILE\n\n"
        f"User: @{u['username']}\n"
        f"ID: `{uid}`\n"
        f"──────────────\n"
        f"State: {u['state']}\n"
        f"Balance: ${u.get('balance', 0):,}\n"
        f"Deposited: ${u.get('total_deposited', 0):,}\n"
        f"Orders: {u.get('orders_count', 0)}\n"
        f"Since: {u['registered_at'][:10]}"
    )
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="Change State", callback_data="profile_change_state"),
            types.InlineKeyboardButton(text="Top Up", callback_data="profile_top_up")
        ],
        [
            types.InlineKeyboardButton(text="Order History", callback_data="profile_orders"),
            types.InlineKeyboardButton(text="Deposit History", callback_data="profile_deposits")
        ],
        [types.InlineKeyboardButton(text="🔐 Security", callback_data="profile_security")]
    ])
    return text, kb


@dp.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    if is_registered(message.from_user.id):
        await message.answer(
            f"👋 *Welcome back!*\n\n📍 Your state: *{get_user_state(message.from_user.id)}*",
            parse_mode="Markdown", reply_markup=get_main_keyboard()
        )
    else:
        await message.answer(
            f"*{SHOP_NAME}*\n\n_No license required._",
            parse_mode="Markdown",
            reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
                [types.InlineKeyboardButton(text="Enter", callback_data="enter_store")]
            ])
        )


@dp.callback_query(F.data == "enter_store")
async def enter_store(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📋 *Verification*\n\nEnter your state:", parse_mode="Markdown")
    await state.set_state(RegistrationState.entering_state)
    await callback.answer()


@dp.message(RegistrationState.entering_state)
async def process_state_input(message: types.Message, state: FSMContext):
    key = find_state_in_list(message.text or "")
    if not key:
        await message.answer("❌ *State not found*\n\nCheck the spelling and try again:", parse_mode="Markdown")
        return
    name = STATES[key]["name"]
    register_user(message.from_user.id, message.from_user.username or "Unknown", name)
    await state.clear()
    await message.answer(
        f"✅ *Access granted.*\n\n📍 State: *{name}*\n\nYou can now explore our store.",
        parse_mode="Markdown", reply_markup=get_main_keyboard()
    )
    await bot.send_message(
        ADMIN_ID,
        f"🆕 *New customer*\n👤 @{message.from_user.username}\n🆔 `{message.from_user.id}`\n📍 {name}",
        parse_mode="Markdown"
    )


@dp.message(Command("stock"))
async def admin_stock(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        return
    args = message.text.split()
    if len(args) != 3 or args[2].lower() not in ("true", "false"):
        await message.answer("Usage: `/stock <code> <true/false>`", parse_mode="Markdown")
        return
    code = args[1].lower()
    if code not in WEAPONS:
        await message.answer(f"❌ `{code}` not found.", parse_mode="Markdown")
        return
    stock = load_json(STOCK_FILE)
    stock[code] = args[2].lower() == "true"
    save_json(STOCK_FILE, stock)
    mark = "✅ IN STOCK" if stock[code] else "❌ OUT OF STOCK"
    await message.answer(f"*{WEAPONS[code]['name']}* → {mark}", parse_mode="Markdown")


@dp.message(F.text == "👤 Profile")
async def show_profile(message: types.Message):
    if not is_registered(message.from_user.id):
        await message.answer("⚠️ Complete registration first with /start")
        return
    text, kb = build_profile(message.from_user.id)
    await message.answer(text, parse_mode="Markdown", reply_markup=kb)


@dp.callback_query(F.data == "back_to_profile")
async def back_to_profile(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    text, kb = build_profile(callback.from_user.id)
    await callback.message.edit_text(text, parse_mode="Markdown", reply_markup=kb)
    await callback.answer()


@dp.callback_query(F.data == "profile_change_state")
async def start_change_state(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "📍 ***Change your state***\n\nEnter the new state name:", parse_mode="Markdown"
    )
    await state.set_state(ProfileState.changing_state)
    await callback.answer()


@dp.message(ProfileState.changing_state)
async def process_change_state(message: types.Message, state: FSMContext):
    key = find_state_in_list(message.text or "")
    if not key:
        await message.answer("❌ *State not found*. Try again:", parse_mode="Markdown")
        return
    name = STATES[key]["name"]
    users = load_users()
    users[str(message.from_user.id)]["state"] = name
    save_users(users)
    await state.clear()
    await message.answer(
        f"✅ State changed to: *{name}*\n\n_Prices and shipping will be recalculated._",
        parse_mode="Markdown", reply_markup=get_main_keyboard()
    )


@dp.callback_query(F.data == "profile_orders")
async def profile_orders(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "📜 ***Order History***\n\n_No completed orders found._",
        parse_mode="Markdown", reply_markup=back_kb()
    )
    await callback.answer()


@dp.callback_query(F.data == "profile_deposits")
async def profile_deposits(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "💳 ***Deposit History***\n\n"
        "📅 **Date** | 💰 **Amount** | ✅ **Status**\n"
        "━━━━━━━━━━━━\n"
        "_No deposits found._",
        parse_mode="Markdown", reply_markup=back_kb()
    )
    await callback.answer()


@dp.callback_query(F.data == "profile_security")
async def profile_security(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "🔐 ***Security Settings***\n\n"
        "🛡️ **2FA Authentication:** `Enabled`\n"
        "🔑 **PGP Key:** `Not set`\n"
        "🔒 **Session Encryption:** `AES-256-GCM`\n"
        "🌐 **Last Login IP:** `Hidden (Proxy)`",
        parse_mode="Markdown", reply_markup=back_kb()
    )
    await callback.answer()


@dp.callback_query(F.data == "profile_top_up")
async def top_up_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        "💰 ***Select Payment Method***\n\n━━━━━━━━━━━━\n⚠️ _Deposit: $9-9999_\n━━━━━━━━━━━━",
        parse_mode="Markdown",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="₿ Bitcoin (BTC)", callback_data="dep_btc")],
            [types.InlineKeyboardButton(text="Ł Litecoin (LTC)", callback_data="dep_ltc")],
            [types.InlineKeyboardButton(text="₮ USDT (TRC-20)", callback_data="dep_usdt")],
            [types.InlineKeyboardButton(text="◀️ Back", callback_data="back_to_profile")]
        ])
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("dep_"))
async def dep_ask_amount(callback: types.CallbackQuery, state: FSMContext):
    coin = callback.data.split("_", 1)[1]
    await state.update_data(coin=coin)
    await callback.message.edit_text(
        "💰 ***Enter Deposit Amount***\n\n"
        "Enter the amount in USD:\n\n⚠️ _Deposit: $9-9999_",
        parse_mode="Markdown"
    )
    await state.set_state(DepositState.waiting_amount)
    await callback.answer()


@dp.message(DepositState.waiting_amount)
async def dep_amount(message: types.Message, state: FSMContext):
    try:
        amount = float((message.text or "").replace(",", ".").replace("$", "").strip())
    except ValueError:
        await message.answer("❌ Enter a valid number (e.g. 100).", parse_mode="Markdown")
        return
    if amount < 9 or amount > 9999:
        await message.answer("❌ Amount must be between *$9* and *$9999*.", parse_mode="Markdown")
        return
    await state.update_data(amount=amount)
    await message.answer(
        f"✅ ***Confirm Deposit***\n\nCreate a deposit for *${amount:,.2f}*?",
        parse_mode="Markdown",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="✅ Yes, Create Deposit", callback_data="depgo")],
            [types.InlineKeyboardButton(text="❌ Cancel", callback_data="profile_top_up")]
        ])
    )


@dp.callback_query(F.data == "depgo")
async def dep_create(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    coin = data.get("coin")
    amount = data.get("amount")
    if not coin or not amount:
        await callback.answer("Session expired", show_alert=True)
        return
    await callback.message.edit_text(
        "⏳ ***Processing...***\n\n🔍 _Verifying wallet details..._", parse_mode="Markdown"
    )
    await callback.answer()
    await asyncio.sleep(3)

    rid = new_request({
        "type": "deposit",
        "user_id": callback.from_user.id,
        "username": callback.from_user.username,
        "amount": amount,
        "coin": coin,
    })
    c = COINS[coin]
    await callback.message.edit_text(
        f"{c['symbol']} ***Deposit Details***\n\n"
        f"━━━━━━━━━━━━\n"
        f"💰 **Amount:** `${amount:,.2f}`\n"
        f"💵 **Send exactly:** `{coin_str(coin, amount)}`\n\n"
        f"📍 **Wallet Address:**\n`{WALLETS[c['wallet']]}`\n"
        f"━━━━━━━━━━━━\n\n"
        f"⚠️ _Send only {c['name']} to this address._",
        parse_mode="Markdown",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="✅ I Paid", callback_data=f"paid_{rid}")],
            [types.InlineKeyboardButton(text="◀️ Back", callback_data="profile_top_up")]
        ])
    )
    await state.clear()


@dp.message(F.text == "🔫 Catalog")
async def show_catalog(message: types.Message):
    if not is_registered(message.from_user.id):
        await message.answer("⚠️ Complete registration first with /start")
        return
    await message.answer("📂 *Catalog*", parse_mode="Markdown", reply_markup=get_catalog_keyboard())


@dp.callback_query(F.data.startswith("cat_"))
async def show_category(callback: types.CallbackQuery):
    key = callback.data.split("_", 1)[1]
    if key == "catalog":
        await callback.message.edit_text("📂 *Catalog*", parse_mode="Markdown", reply_markup=get_catalog_keyboard())
        await callback.answer()
        return
    items = {code: w for code, w in WEAPONS.items() if w["category"] == key}
    rows = [[types.InlineKeyboardButton(text=w["name"], callback_data=f"weapon_{code}")] for code, w in items.items()]
    rows.append([types.InlineKeyboardButton(text="◀️ Back", callback_data="cat_catalog")])
    await callback.message.edit_text(
        f"*{CATEGORIES.get(key, key)}*", parse_mode="Markdown",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=rows)
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("weapon_"))
async def weapon_checkout(callback: types.CallbackQuery):
    code = callback.data.split("_", 1)[1]
    w = WEAPONS.get(code)
    if not w:
        await callback.answer("Item not found", show_alert=True)
        return
    back = "cat_catalog" if code == "glock_switch" else f"cat_{w['category']}"

    if not is_in_stock(code):
        await callback.message.edit_text(
            f"{w['name']}\n\nThis item is temporarily out of stock.",
            parse_mode="Markdown", reply_markup=back_kb(back, "Back")
        )
        await callback.answer()
        return

    sk = get_state_key_by_name(get_user_state(callback.from_user.id))
    if not sk:
        await callback.answer("State not found", show_alert=True)
        return

    item = calculate_price(w["base_price"], sk, w["fixed_price"])
    ship = get_shipping_cost(code, sk)
    total = item + ship
    days = get_shipping_days(sk, code)

    if code == "glock_switch":
        desc = "Made from aluminum.\n"
        cond = "New"
    else:
        desc = ""
        cond = "Unfired / no signs of wea"

    caption = (
        f"CHECKOUT\n\n"
        f"{w['name']}\n"
        f"{desc}\n"
        f"Condition: {cond}\n"
        f"Carrier: USPS\n"
        f"Destination: {STATES[sk]['name']}\n"
        f"Delivery: {days} business days\n"
        f"──────────────\n"
        f"Item: ${item:,}\n"
        f"Shipping: ${ship:,}\n"
        f"──────────────\n"
        f"Total: ${total:,}"
    )
    kb = types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="Balance", callback_data=f"pay_balance_{code}")],
        [types.InlineKeyboardButton(text="₿ Bitcoin", callback_data=f"pay_btc_{code}")],
        [types.InlineKeyboardButton(text="Ł Litecoin", callback_data=f"pay_ltc_{code}")],
        [types.InlineKeyboardButton(text="₮ USDT TRC-20", callback_data=f"pay_usdt_{code}")],
        [types.InlineKeyboardButton(text="Back", callback_data=back)]
    ])

    img = f"images/{w.get('image') or (code + '.jpg')}"
    if os.path.exists(img):
        await callback.message.delete()
        await callback.message.answer_photo(
            photo=types.FSInputFile(img), caption=caption,
            parse_mode="Markdown", reply_markup=kb
        )
    else:
        await callback.message.edit_text(caption, parse_mode="Markdown", reply_markup=kb)
    await callback.answer()


@dp.callback_query(F.data.startswith("pay_"))
async def pay_handler(callback: types.CallbackQuery, state: FSMContext):
    method, code = callback.data[4:].split("_", 1)
    w = WEAPONS.get(code)
    if not w:
        await callback.answer("Item not found", show_alert=True)
        return
    if not is_in_stock(code):
        await callback.answer("Out of stock", show_alert=True)
        return
    sk = get_state_key_by_name(get_user_state(callback.from_user.id))
    if not sk:
        await callback.answer("State not found", show_alert=True)
        return

    item = calculate_price(w["base_price"], sk, w["fixed_price"])
    ship = get_shipping_cost(code, sk)
    total = item + ship
    days = get_shipping_days(sk, code)
    uid = callback.from_user.id
    users = load_users()
    balance = users[str(uid)].get("balance", 0)

    if method == "balance":
        if balance < total:
            await callback.answer(
                f"❌ Insufficient balance\nRequired: ${total:,}\nBalance: ${balance:,}",
                show_alert=True
            )
            return
        users[str(uid)]["balance"] -= total
        users[str(uid)]["orders_count"] += 1
        save_users(users)
        rid = new_request({
            "type": "order",
            "user_id": uid,
            "username": callback.from_user.username,
            "weapon_name": w["name"],
            "amount": total,
            "state": STATES[sk]["name"],
            "delivery": days,
            "payment_method": "Balance",
        })
        await send_order_to_admin(callback, rid)
        await callback.message.edit_text(
            f"✅ ***Order Submitted***\n\n🔫 {w['name']}\n💵 `${total:,}` paid from balance.\n\n"
            f"📩 _Awaiting confirmation._",
            parse_mode="Markdown", reply_markup=back_kb()
        )
        await callback.answer()
        return

    if method not in COINS:
        await callback.answer("Unknown method", show_alert=True)
        return

    await callback.message.edit_text(
        "⏳ ***Processing...***\n\n🔍 _Verifying wallet details..._", parse_mode="Markdown"
    )
    await callback.answer()
    await asyncio.sleep(3)

    rid = new_request({
        "type": "order",
        "user_id": uid,
        "username": callback.from_user.username,
        "weapon_name": w["name"],
        "amount": total,
        "state": STATES[sk]["name"],
        "delivery": days,
        "coin": method,
        "payment_method": method.upper(),
    })
    c = COINS[method]
    await callback.message.edit_text(
        f"{c['symbol']} ***Order Payment***\n\n"
        f"━━━━━━━━━━━━\n"
        f"🔫 **Item:** {w['name']}\n"
        f"💰 **Amount:** `${total:,.2f}`\n"
        f"💵 **Send exactly:** `{coin_str(method, total)}`\n\n"
        f"📍 **Wallet Address:**\n`{WALLETS[c['wallet']]}`\n"
        f"━━━━━━━━━━━━\n\n"
        f"⚠️ _Send only {c['name']} to this address._",
        parse_mode="Markdown",
        reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="✅ I Paid", callback_data=f"paid_{rid}")],
            [types.InlineKeyboardButton(text="◀️ Back", callback_data=f"weapon_{code}")]
        ])
    )
    await state.clear()


async def send_order_to_admin(callback, rid):
    r = load_requests()[rid]
    msg = (
        f"🚨 ***NEW PURCHASE REQUEST*** 🚨\n\n"
        f"👤 **User:** @{r['username']}\n"
        f"🆔 **ID:** `{r['user_id']}`\n"
        f"🔫 **Item:** {r['weapon_name']}\n"
        f"💵 **Amount:** `${r['amount']:,.2f}`\n"
        f"💳 **Payment:** {r['payment_method']}\n"
        f"📍 **State:** {r['state']}\n"
        f"📅 **Delivery:** {r['delivery']} business days\n\n"
        f"━━━━━━━━━━━━\n"
        f"🆔 `{rid}`"
    )
    await bot.send_message(ADMIN_ID, msg, parse_mode="Markdown", reply_markup=admin_kb(rid))


@dp.callback_query(F.data.startswith("paid_"))
async def paid(callback: types.CallbackQuery):
    rid = callback.data.split("_", 1)[1]
    reqs = load_requests()
    r = reqs.get(rid)
    if not r:
        await callback.answer("Request not found", show_alert=True)
        return
    if r["status"] != "pending":
        await callback.answer("Already processed", show_alert=True)
        return

    if r["type"] == "deposit":
        msg = (
            f"💰 ***NEW DEPOSIT REQUEST*** 💰\n\n"
            f"👤 **User:** @{r['username']}\n"
            f"🆔 **ID:** `{r['user_id']}`\n"
            f"💵 **Amount:** `${r['amount']:,.2f}`\n"
            f"💳 **Coin:** {r['coin'].upper()}\n"
            f"📍 **Type:** Balance Top-Up\n\n"
            f"━━━━━━━━━━━━\n"
            f"🆔 `{rid}`"
        )
        await bot.send_message(ADMIN_ID, msg, parse_mode="Markdown", reply_markup=admin_kb(rid))
    else:
        await send_order_to_admin(callback, rid)

    await callback.message.edit_text(
        "✅ ***Request Submitted***\n\n📩 _Awaiting verification._",
        parse_mode="Markdown", reply_markup=back_kb()
    )
    await callback.answer()


@dp.callback_query(F.data.startswith("admok_"))
async def admin_ok(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Access denied", show_alert=True)
        return
    rid = callback.data.split("_", 1)[1]
    reqs = load_requests()
    r = reqs.get(rid)
    if not r:
        await callback.answer("Request not found", show_alert=True)
        return
    if r["status"] != "pending":
        await callback.answer(f"Already {r['status']}", show_alert=True)
        return

    r["status"] = "confirmed"
    save_requests(reqs)
    uid = str(r["user_id"])
    users = load_users()

    if r["type"] == "deposit":
        users[uid]["balance"] = users[uid].get("balance", 0) + r["amount"]
        users[uid]["total_deposited"] = users[uid].get("total_deposited", 0) + r["amount"]
        save_users(users)
        note = (
            f"✅ ***Deposit Confirmed***\n\n"
            f"*${r['amount']:,.2f}* credited.\n\n"
            f"💰 **Balance:** `${users[uid]['balance']:,.2f}`"
        )
    else:
        if r["payment_method"] != "Balance":
            users[uid]["orders_count"] = users[uid].get("orders_count", 0) + 1
            save_users(users)
        note = (
            f"✅ ***Purchase Confirmed***\n\n"
            f"🔫 {r['weapon_name']}\n"
            f"📍 {r['state']}\n"
            f"📅 {r['delivery']} business days"
        )

    try:
        await bot.send_message(r["user_id"], note, parse_mode="Markdown")
        await callback.message.edit_text(f"✅ *Confirmed*\n\n@{r['username']} notified.\n🆔 `{rid}`", parse_mode="Markdown")
    except Exception as e:
        logging.error(e)
        await callback.message.edit_text(f"⚠️ Saved, but notify failed: {e}")
    await callback.answer()


@dp.callback_query(F.data.startswith("admno_"))
async def admin_no(callback: types.CallbackQuery):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("Access denied", show_alert=True)
        return
    rid = callback.data.split("_", 1)[1]
    reqs = load_requests()
    r = reqs.get(rid)
    if not r:
        await callback.answer("Request not found", show_alert=True)
        return
    if r["status"] != "pending":
        await callback.answer(f"Already {r['status']}", show_alert=True)
        return

    r["status"] = "declined"
    save_requests(reqs)
    uid = str(r["user_id"])

    if r["type"] == "order" and r["payment_method"] == "Balance":
        users = load_users()
        users[uid]["balance"] = users[uid].get("balance", 0) + r["amount"]
        users[uid]["orders_count"] = max(0, users[uid].get("orders_count", 0) - 1)
        save_users(users)

    if r["type"] == "deposit":
        note = f"❌ ***Deposit Declined***\n\nYour deposit request for *${r['amount']:,.2f}* was declined."
    else:
        note = f"❌ ***Purchase Declined***\n\nYour order for *{r['weapon_name']}* was declined."

    try:
        await bot.send_message(r["user_id"], note, parse_mode="Markdown")
        await callback.message.edit_text(f"❌ *Declined*\n\n@{r['username']} notified.\n🆔 `{rid}`", parse_mode="Markdown")
    except Exception as e:
        logging.error(e)
        await callback.message.edit_text(f"⚠️ Saved, but notify failed: {e}")
    await callback.answer()


@dp.message(F.text == "📦 Purchases")
async def show_purchases(message: types.Message):
    if not is_registered(message.from_user.id):
        await message.answer("⚠️ Complete registration first with /start")
        return
    await message.answer("❌ Unfortunately, you have no purchases yet.")


@dp.message(F.text == "🆘 Support")
async def show_support(message: types.Message):
    await message.answer("📞", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="📞 Open Support Chat", url=OPERATOR_LINK)]
    ]))


@dp.message(F.text == "⭐ Reviews")
async def show_reviews(message: types.Message):
    await message.answer("⭐", reply_markup=types.InlineKeyboardMarkup(inline_keyboard=[
        [types.InlineKeyboardButton(text="⭐ Leave a Review", url=REVIEWS_BOT_LINK)]
    ]))


async def main():
    print(f"✅ {SHOP_NAME} bot is running!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())