import math
from datamodel import OrderDepth, UserId, TradingState, Order, Listing, Trade
from typing import List
import numpy as np
import string


class Trader:

    price_history = {str: []}
    quantity_limits = {'STARFRUIT': 20, 'AMETHYSTS': 20, 'ORCHIDS': 100, 'CHOCOLATE': 250, 'STRAWBERRIES': 350, 'ROSES': 60, 'GIFT_BASKET': 60}
    prev_sunlight = 3000
    prev_mvmt = 0

    def run(self, state: TradingState):
        # Only method required. It takes all buy and sell orders for all symbols as an input, and outputs a list of orders to be sent
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
        result = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []

            ask_price = list(order_depth.sell_orders.items())[0][0]
            bid_price = list(order_depth.buy_orders.items())[0][0]

            if product == 'ORCHIDS':
                pass
                try:
                    q = state.position[product]
                except:
                    q = 0
                limit = self.quantity_limits[product]
                print("Product : " + str(product))
                print("Acceptable bid : " + str(bid_price))
                print("Acceptable ask : " + str(ask_price))
                print("Quantity : " + str(q))
                print("Limit : " + str(limit))
                print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(
                    len(order_depth.sell_orders)))
                sunlight = state.observations.conversionObservations[product].sunlight
                if sunlight/self.prev_sunlight > 1:
                    self.prev_mvmt = 1
                    print("BUY", str(limit-abs(q)) + "x", ask_price)
                    orders.append(Order(product, ask_price, limit-abs(q)))
                if sunlight/self.prev_sunlight < 1:
                    self.prev_mvmt = -1
                    print("SELL", str(limit-abs(q)) + "x", bid_price)
                    orders.append(Order(product, bid_price, -limit+abs(q)))
                print("Previous Sunlight : " + str(self.prev_sunlight))
                print("Current Sunlight : " + str(sunlight))
                print("Previous movement : " + str(self.prev_mvmt))
                self.prev_sunlight = sunlight

            elif product == 'STARFRUIT' or product == 'AMETHYSTS':
                s = (ask_price + bid_price) / 2
                try:
                    q = state.position[product]
                except:
                    q = 0

                gamma = 0.01
                var = 0.1
                k = 0.9
                T = 999900

                if int(s) != 0:
                    prices = self.price_history.get(product, [])
                    prices.append(s)
                    self.price_history.update({product: prices})

                lookback = 10
                if len(self.price_history.get(product, [])) >= lookback:
                    var = np.var(self.price_history.get(product)[-1:-lookback:-1])

                r = s - (q * gamma * var * (1 - state.timestamp/T))
                delta = (gamma * var * (1 - state.timestamp/T) + (2 / gamma * math.log(1 + gamma/k)))

                acc_ask = math.ceil(r + delta/2)
                acc_bid = math.ceil(r - delta/2)

                limit = self.quantity_limits[product]

                print("Product : " + str(product))
                print("Acceptable bid : " + str(acc_bid))
                print("Acceptable ask : " + str(acc_ask))
                print("Quantity : " + str(q))
                print("Limit : " + str(limit))
                print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(
                    len(order_depth.sell_orders)))

                if len(order_depth.sell_orders) != 0:
                    for best_ask, best_ask_amount in list(order_depth.sell_orders.items()):
                        if int(best_ask) < acc_ask:
                            print("BUY", str(-max(best_ask_amount, -limit+q)) + "x", best_ask)
                            orders.append(Order(product, best_ask, -max(best_ask_amount, -limit+q)))

                if len(order_depth.buy_orders) != 0:
                    for best_bid, best_bid_amount in list(order_depth.buy_orders.items()):
                        if int(best_bid) > acc_bid:
                            print("SELL", str(min(best_bid_amount, limit-q)) + "x", best_bid)
                            orders.append(Order(product, best_bid, -min(best_bid_amount, limit-q)))

            result[product] = orders

        traderData = "Trade " + str(state.timestamp)  # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.

        conversions = 1
        return result, conversions, traderData
