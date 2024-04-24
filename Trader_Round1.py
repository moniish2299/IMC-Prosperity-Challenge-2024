import math
from datamodel import OrderDepth, UserId, TradingState, Order, Listing, Trade
from typing import List
import numpy as np
import string


class Trader:

    price_history = {str: []}

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

            s = (ask_price + bid_price) / 2
            try:
                q = state.position[product]
            except:
                q = 0

            gamma = 0.01
            var = 0.1
            k = 0.9
            T = 999900

            # if int(s) != 0:
            #     prices = self.price_history.get(product, [])
            #     prices.append(s)
            #     self.price_history.update({product: prices})
            #
            # lookback = 10
            # if len(self.price_history.get(product, [])) >= lookback:
            #     var = np.var(self.price_history.get(product))

            r = s - (q * gamma * var * (1 - state.timestamp/T))
            delta = (gamma * var * (1 - state.timestamp/T) + (2 / gamma * math.log(1 + gamma/k)))

            acc_ask = math.ceil(r + delta/2)
            acc_bid = math.ceil(r - delta/2)

            print("Acceptable bid : " + str(acc_bid))
            print("Acceptable ask : " + str(acc_ask))
            print("Buy Order depth : " + str(len(order_depth.buy_orders)) + ", Sell order depth : " + str(
                len(order_depth.sell_orders)))

            if len(order_depth.sell_orders) != 0:
                for best_ask, best_ask_amount in list(order_depth.sell_orders.items()):
                    if int(best_ask) < acc_ask:
                        print("BUY", str(-best_ask_amount) + "x", best_ask)
                        orders.append(Order(product, best_ask, -best_ask_amount))

            if len(order_depth.buy_orders) != 0:
                for best_bid, best_bid_amount in list(order_depth.buy_orders.items()):
                    if int(best_bid) > acc_bid:
                        print("SELL", str(best_bid_amount) + "x", best_bid)
                        orders.append(Order(product, best_bid, -best_bid_amount))

            result[product] = orders

        traderData = "Trade " + str(state.timestamp)  # String value holding Trader state data required. It will be delivered as TradingState.traderData on next execution.

        conversions = 1
        return result, conversions, traderData

# timestamp = 1100
#
# listings = {
#     "PRODUCT1": Listing(
#         symbol="PRODUCT1",
#         product="PRODUCT1",
#         denomination="SEASHELLS"
#     ),
#     "PRODUCT2": Listing(
#         symbol="PRODUCT2",
#         product="PRODUCT2",
#         denomination="SEASHELLS"
#     ),
# }
#
# order_depths = {
#     "PRODUCT1": OrderDepth(),
#     "PRODUCT2": OrderDepth(),
# }
# order_depths['PRODUCT1'].buy_orders = {10: 7, 9: 5}
# order_depths['PRODUCT1'].sell_orders = {12: -5, 13: -3}
# order_depths['PRODUCT2'].buy_orders={142: 3, 141: 5}
# order_depths['PRODUCT2'].sell_orders={144: -5, 145: -8}
#
#
# own_trades = {
#     "PRODUCT1": [
#         Trade(
#             symbol="PRODUCT1",
#             price=11,
#             quantity=4,
#             buyer="SUBMISSION",
#             seller="",
#             timestamp=1000
#         ),
#         Trade(
#             symbol="PRODUCT1",
#             price=12,
#             quantity=3,
#             buyer="SUBMISSION",
#             seller="",
#             timestamp=1000
#         )
#     ],
#     "PRODUCT2": [
#         Trade(
#             symbol="PRODUCT2",
#             price=143,
#             quantity=2,
#             buyer="",
#             seller="SUBMISSION",
#             timestamp=1000
#         ),
#     ]
# }
#
# market_trades = {
#     "PRODUCT1": [],
#     "PRODUCT2": []
# }
#
# position = {
#     "PRODUCT1": 10,
#     "PRODUCT2": -7
# }
#
# observations = {}
#
# traderData = ""
#
# state1 = TradingState(
#     traderData,
#     timestamp,
#     listings,
#     order_depths,
#     own_trades,
#     market_trades,
#     position,
#     observations
# )
#
# # mock_trader = Trader()
# # mock_trader.run(state1)
