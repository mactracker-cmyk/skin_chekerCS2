import requests
import json
import time

STEAM_API_KEY = "YOUR_STEAM_API_KEY"  # Замените на ваш Steam API ключ
STEAM_ID64 = "76561198191871290"  # Пример SteamID64 пользователя
CS2_APP_ID = 730  # App ID для CS2
INVENTORY_URL = "http://steamcommunity.com/inventory/{}/730/2?l=english&count=5000"
MARKET_PRICE_URL = "http://steamcommunity.com/market/priceoverview/?appid=730&currency=1&market_hash_name={}"


def get_user_inventory(steam_id):
    """Получение инвентаря пользователя из Steam API."""
    try:
        response = requests.get(INVENTORY_URL.format(steam_id))
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении инвентаря: {e}")
        return None


def get_market_price(market_hash_name):
    """Получение цены предмета с Steam Community Market."""
    try:
        response = requests.get(MARKET_PRICE_URL.format(market_hash_name))
        response.raise_for_status()
        data = response.json()
        if data.get("success"):
            return {
                "lowest_price": data.get("lowest_price", "N/A"),
                "median_price": data.get("median_price", "N/A"),
                "volume": data.get("volume", "N/A")
            }
        return {"lowest_price": "N/A", "median_price": "N/A", "volume": "N/A"}
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении цены для {market_hash_name}: {e}")
        return {"lowest_price": "N/A", "median_price": "N/A", "volume": "N/A"}


def main():
    inventory_data = get_user_inventory(STEAM_ID64)
    if not inventory_data or "descriptions" not in inventory_data:
        print("Не удалось получить инвентарь. Проверьте SteamID или настройки приватности.")
        return

    # Список для хранения информации о скинах
    skins = []

    # Обработка предметов
    for item in inventory_data.get("descriptions", []):
        # Проверяем, что предмет относится к CS2 и имеет рыночное название
        if item.get("appid") == CS2_APP_ID and item.get("marketable", 0) == 1:
            market_hash_name = item.get("market_hash_name", "")
            if market_hash_name:
                # Получение цены с рынка
                price_data = get_market_price(market_hash_name)
                skin_info = {
                    "name": item.get("name", "Unknown"),
                    "market_hash_name": market_hash_name,
                    "type": item.get("type", "Unknown"),
                    "rarity": item.get("tags", [{}])[0].get("localized_tag_name", "Unknown"),
                    "lowest_price": price_data["lowest_price"],
                    "median_price": price_data["median_price"],
                    "volume": price_data["volume"]
                }
                skins.append(skin_info)
                print(f"Обработан скин: {skin_info['name']}")
                time.sleep(2)

    with open("cs2_inventory.json", "w", encoding="utf-8") as f:
        json.dump(skins, f, indent=4, ensure_ascii=False)
    print(f"Данные сохранены в cs2_inventory.json. Найдено скинов: {len(skins)}")


if __name__ == "__main__":
    main()
