import math
from datamodel import OrderDepth, UserId, TradingState, Order
from typing import List
import numpy as np
import string


class Trader:

    mid_prices = []

    def run(self, state: TradingState):
        # Only method required. It takes all buy and sell orders for all symbols as an input, and outputs a list of orders to be sent
        print("traderData: " + state.traderData)
        print("Observations: " + str(state.observations))
        result = {}
        for product in state.order_depths:
            order_depth: OrderDepth = state.order_depths[product]
            orders: List[Order] = []
            acc_bid, acc_ask = self.determine_price(order_depth, state.position[product], state.timestamp)  # Participant should calculate this value
            print("Acceptable bid : " + str(acc_bid))
            print("Acceptable ask : " + str(acc_ask))
            print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(
                len(order_depth.sell_orders)))

            if len(order_depth.sell_orders) != 0:
                best_ask, best_ask_amount = list(order_depth.sell_orders.items())[0]
                if int(best_ask) < acc_ask:
                    print("BUY", str(-best_ask_amount) + "x", best_ask)
                    orders.append(Order(product, best_ask, -best_ask_amount))

            if len(order_depth.buy_orders) != 0:
                best_bid, best_bid_amount = list(order_depth.buy_orders.items())[0]
                if int(best_bid) > acc_bid:
                    print("SELL", str(best_bid_amount) + "x", best_bid)
                    orders.append(Order(product, best_bid, -best_bid_amount))

            result[product] = orders

        traderData = "SAMPLE"  # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.

        conversions = 1
        return result, conversions, traderData

    def determine_price(self, order_depth, position, timestamp):
        buy_orders = order_depth.buy_orders
        sell_orders = order_depth.sell_orders

        s = (list(buy_orders.keys())[0] + list(sell_orders.keys())[0]) / 2

        q = 0
        gamma = 0.05
        var = 0
        k = 1
        T = 99900

        if s != 0:
            self.mid_prices.append(s)

        lookback = 10
        if len(self.mid_prices) >= lookback:
            var = np.var(self.mid_prices[-1:-lookback - 1:-1])
            q = position

        r = s - (q * gamma * var * (T - timestamp)/T)
        print(r)

        delta = (gamma * var * (T - timestamp)/T + (2 / gamma * math.log(1 + (gamma / k))))
        print(delta)

        new_bid = math.ceil((r - delta)/2)
        new_ask = math.ceil((r + delta)/2)

        return new_bid, new_ask
