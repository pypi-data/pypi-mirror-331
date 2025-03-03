# growwapi SDK API Documentation

## Overview

`gwapex_base` is the foundational SDK for accessing Groww APIs and listening to live data streams. This package provides the core functionalities to interact with Groww's trading platform.

## Features

- Connect to Groww's API
- Place, modify, and cancel orders
- Retrieve order details, status, holdings, trade lists
- Subscribe and unsubscribe to market feeds
- Get live market data and updates

## Installation

Install the package using pip:

```bash
pip install growwapi
```

## Usage

### Authentication

To use the SDK, you need to authenticate using your API credentials. Set the following variables:

- `API_AUTH_TOKEN`: Your API authentication token.

### API Client

The `GrowwAPI` class provides [methods to interact with the Groww API](#api-methods).

```python
from growwapi import GrowwAPI

groww_client = GrowwAPI("YOUR_API_KEY")

# Get the current orders. Will wait for 5 seconds or until the orders are received
orders = groww_client.get_order_list(timeout=5)
print(orders)
```

### Feed Client

The `GrowwFeed` class provides [methods to subscribe to and receive Groww data streams and updates](#feed-methods).

It can either be used synchronously to get the last updated data or asynchronously to trigger a callback whenever new data is received.

```python
from growwapi import GrowwFeed

groww_feed = GrowwFeed("YOUR_API_KEY")

# Synchronous Usage: Create a subscription and then get the LTP
groww_feed.subscribe_stocks_live("SWIGGY")
# Will wait for 3 seconds or until the LTP is received
ltp = groww_feed.get_stocks_ltp("SWIGGY", timeout=3)
print(ltp)


# Asynchronous Usage: Callback triggered whenever the LTP changes
def get_ltp_print():
  # As it was triggerred on data received, we can directly get the LTP
  ltp = groww_feed.get_stocks_ltp("RELIANCE")
  print(ltp)


groww_feed.subscribe_stocks_live("RELIANCE", on_data_received=get_ltp_print)
```

## API Methods

The SDK provides methods to interact with the Groww API using the `GrowwAPI` class accessible from the `gwapex_base` module.

All API methods take an additional `timeout` parameter to specify the maximum time to wait for a response from the API. If the response is not received within the specified time, a [GrowwAPITimeoutException](#growwclienttimeoutexception) is raised.

### Get Current Orders

Fetch and log the current orders.

```python
# To fetch Orders from all segments
orders = groww_client.get_order_list(timeout=5)

# To fetch Orders from a specific segment
orders_cash = groww_client.get_order_list(segment=GrowwAPI.SEGMENT_CASH)
print(orders_cash)
```

#### Get Current Orders - Request Fields

- `segment` (str): The segment of the orders to retrieve. If not provided, orders from all segments are fetched.

#### Get Current Orders - Response Fields

- `orderList` (list[[OrderDetailDto](#orderdetaildto)]): A list of orders.

### Get Latest Index Data

Fetch the latest data for an index.

```python
latest_index_data = groww_client.get_latest_index_data(
        exchange=GrowwAPI.EXCHANGE_NSE,
        segment=GrowwAPI.SEGMENT_CASH,
        symbol="NIFTY",
        timeout=5
)
print(latest_index_data)
```

#### Get Latest Index Data - Request Fields

- `exchange` (str): The exchange of the instrument.
- `segment` (str): The segment of the instrument.
- `symbol` (str): The symbol of the index.

#### Get Latest Index Data - Response Fields

The response will have the same fields as [LiveIndexData](#liveindexdata).

### Get Quote of an instrument.

Fetch the quote data for an instrument.

```python
latest_price_data = groww_client.get_quote(
        exchange=GrowwAPI.EXCHANGE_NSE,
        segment=GrowwAPI.SEGMENT_CASH,
        trading_symbol="SWIGGY",
        timeout=5
)
print(latest_price_data)
```

#### Get Latest Price - Request Fields

- `exchange` (str): The exchange of the instrument.
- `segment` (str): The segment of the instrument.
- `symbol` (str): The symbol of the instrument.

#### Get Latest Price - Response Fields

The response will have the same fields as [LivePriceData](#livepricedata).

### Get Market Depth

Fetch the market depth data for an instrument.

```python
from growwapi.groww.enums import Exchange, Segment

market_depth_data = groww_client.get_market_depth(
    exchange=GrowwAPI.EXCHANGE_NSE,
    segment=GrowwAPI.SEGMENT_CASH,
    symbol="SWIGGY",
    timeout=5
)
print(market_depth_data)
```

#### Get Market Depth - Request Fields

- `exchange` (str): The exchange of the instrument.
- `segment` (str): The segment of the instrument.
- `symbol` (str): The symbol of the instrument.

#### Get Market Depth - Response Fields

The response will have the same fields as [MarketDepthData](#marketdepthdata).

### Get LTP

Fetch the LTP data for an instrument.

```python
from gwapex_base.groww.enums import Exchange, Segment

ltp_data = groww_client.get_ltp(
    exchange=Exchange.NSE,
    segment=Segment.CASH,
    symbol="SWIGGY",
    timeout=5
)
print(ltp_data)
```

#### Get LTP - Request Fields

- `exchange` ([Exchange](#exchange)): The exchange of the instrument.
- `segment` ([Segment](#segment)): The segment of the instrument.
- `symbol` (str): The symbol of the instrument.

#### Get LTP - Response Fields

The response will have the same fields as [LtpData](#ltpdata).

### Get Index LTP

Fetch the latest LTP data for an index.

```python
from gwapex_base.groww.enums import Exchange, Segment

ltp_data = groww_client.get_index_ltp(
    exchange=Exchange.NSE,
    segment=Segment.CASH,
    symbol="NIFTY",
    timeout=5
)
print(ltp_data)
```

#### Get Index LTP - Request Fields

- `exchange` ([Exchange](#exchange)): The exchange of the index.
- `segment` ([Segment](#segment)): The segment of the index.
- `symbol` (str): The symbol of the index.

#### Get Index LTP - Response Fields

The response will have the same fields as [IndexLtpData](#indexltpdata).

### Place Order

Place a new order.

```python
order_response = groww_client.place_order(
        validity=GrowwAPI.VALIDITY_DAY,
        exchange=GrowwAPI.EXCHANGE_NSE,
        transaction_type=GrowwAPI.TRANSACTION_TYPE_BUY,
        order_type=GrowwAPI.ORDER_TYPE_MARKET,
        price=1,
        product=GrowwAPI.PRODUCT_MIS,
        quantity=10,
        segment=GrowwAPI.SEGMENT_CASH,
        trading_symbol="RELIANCE-EQ",
)
print(order_response)
```

#### Place Order - Request Fields

- `validity` ([Validity](#validity)): The validity of the order.
- `exchange` (str): The exchange where the order is placed.
- `transaction_type` ([TransactionType](#transactiontype)): The type of transaction.
- `order_type` (str): The type of order.
- `price` (float): The price of the order.
- `product` (str): The product type of the order.
- `qty` (int): The quantity of the order.
- `segment` (str): The segment of the order.
- `tradingSymbol` (str): The trading symbol of the order.

#### Place Order - Response Fields

- `growwOrderId` (str): The Groww order ID.
- `orderReferenceId` (Optional[str]): The order reference ID.
- `orderStatus` (str): The status of the order.
- `remark` (Optional[str]): Any remarks for the order.

### Modify Order

Modify an existing order.

```python
modify_order_response = groww_client.modify_order(
    groww_order_id=order_response.groww_order_id,
    order_reference_id=order_response.order_reference_id,
    order_type=OrderType.LIMIT,
    price=3,
    qty=20,
    segment=GrowwAPI.SEGMENT_CASH,
)
print(modify_order_response)
```

#### Modify Order - Request Fields

- `growwOrderId` (Optional[str]): The Groww order ID.
- `orderReferenceId` (Optional[str]): The order reference ID.
- `orderType` (str): The type of order.
- `price` (float): The price of the order.
- `qty` (int): The quantity of the order.
- `segment` (str): The segment of the order.

#### Modify Order - Response Fields

- `growwOrderId` (str): The Groww order ID.
- `orderReferenceId` (Optional[str]): The order reference ID.
- `orderStatus` (str): The status of the order.
- `remark` (Optional[str]): Any remarks for the order.

### Cancel Order

Cancel an existing order.

```python
cancel_response = groww_client.cancel_order(
    groww_order_id=order_response.groww_order_id,
    order_reference_id=order_response.order_reference_id,
    segment=GrowwAPI.SEGMENT_CASH,
)
print(cancel_response)
```

#### Cancel Order - Request Fields

- `growwOrderId` (str): The Groww order ID.
- `orderReferenceId` (Optional[str]): The order reference ID.
- `segment` (str): The segment of the order.

#### Cancel Order - Response Fields

- `growwOrderId` (str): The Groww order ID.
- `orderReferenceId` (Optional[str]): The order reference ID.
- `orderStatus` (str): The status of the order.
- `remark` (Optional[str]): Any remarks for the order.

### Get Holdings

Fetch and log the user's holdings.

```python
holdings_response = groww_client.get_holdings_for_user()
print(holdings)
```

#### Get Holdings - Response Fields

- `holdings` (list[[Holding](#holding)]): A list of holdings.

### Get Order Details

Get and log the details of an order using the Groww order ID.

```python
order_details = groww_client.get_order_detail(
    groww_order_id=order_response.groww_order_id,
    segment=GrowwAPI.SEGMENT_CASH,
)
print(order_details)
```

#### Get Order Details - Request Fields

- `growwOrderId` (Optional[str]): The Groww order ID.
- `orderReferenceId` (Optional[str]): The order reference ID.
- `segment` (str): The segment of the order.

#### Get Order Details - Response Fields

Exactly the same fields as [OrderDetailDto](#orderdetaildto).

### Get Positions

Fetch and log the user's positions.

```python
from growwapi.groww.enums import Segment

positions = groww_client.get_positions_for_user(segment=GrowwAPI.SEGMENT_CASH, )
print(positions)
```

#### Get Positions - Request Fields

- `segment` (str): The segment of the positions to retrieve.

#### Get Positions - Response Fields

- `symbolWisePositions` (dict[str, dict]): A dictionary of symbol-wise positions.
  - `symbolIsin` (Optional[str]): The ISIN of the symbol.
  - `productWisePositions` (dict[str, dict]): A dictionary of product-wise positions.
    - `exchangePosition` (dict[str, [PositionDetailDto](#positiondetaildto)]): A dictionary of exchange-wise positions.

### Get Position for Symbol

Fetch and log the user's positions for a symbol.

```python
positions = groww_client.get_position_for_symbol(symbol_isin="INE221H01019")
print(positions)
```

#### Get Position for Symbol - Request Fields

- `symbolIsin` (str): The ISIN of the symbol.

#### Get Position for Symbol - Response Fields

- `symbolWisePositions` (dict[str, dict]): A dictionary of symbol-wise positions.
  - `symbolIsin` (Optional[str]): The ISIN of the symbol.
  - `productWisePositions` (dict[str, [ExchangePosition](#exchangeposition)]): A dictionary of product-wise exchange positions.

### Get Trade List for Order

Fetch and log the trade list for an order.

```python
trade_response = groww_client.get_trade_list_for_order(
    groww_order_id=order_response.groww_order_id,
    segment=GrowwAPI.SEGMENT_CASH,
)
print(trade_response)
```

#### Get Trade List for Order - Request Fields

- `growwOrderId` (str): The Groww order ID.
- `segment` (str): The segment of the order.

#### Get Trade List for Order - Response Fields

- `tradeList` (list[[Trade](#trade)]): A list of trades.

## Feed Methods

The SDK provides methods to subscribe to and receive live data streams using the `GrowwFeed` class accessible from the `gwapex_base` module.

All feed methods take an additional `timeout` parameter to specify the maximum time to wait for a response from the feed. If the response is not received within the specified time, a `None` is returned.

### Live Data

#### Derivatives Live Data

Subscribe to, get, and unsubscribe from the live data of a derivatives contract.

```python
derivatives_symbol = "NIFTY24DECFUT"
groww_feed.subscribe_derivatives_live(derivatives_symbol)
live = groww_feed.get_derivatives_live(derivatives_symbol)
print(live)
# Or to get just the LTP
print(groww_feed.get_derivatives_ltp(derivatives_symbol))
groww_feed.unsubscribe_derivatives_live(derivatives_symbol)
```

##### Derivative Live Data - Request Fields

- `subscription_key` (str): The subscription key.

##### Derivative Live Data - Response Fields

Returns an Optional[[LivePriceData](#livepricedata)] which has the live price data.

#### Indices Live Data

Subscribe to, get, and unsubscribe from the live data of an index.

```python
index_symbol = "NIFTY"
groww_feed.subscribe_indices_live(index_symbol)
live = groww_feed.get_indices_live(index_symbol)
print(live)
# Or to get just the value
print(groww_feed.get_indices_value(index_symbol))
groww_feed.unsubscribe_indices_live(index_symbol)
```

##### Live Index Data - Request Fields

- `subscription_key` (str): The subscription key.

##### Live Index Data - Response Fields

Returns an Optional[[LiveIndexData](#liveindexdata)] which contains the live index data.

#### Stocks Live Data

Subscribe to, get, and unsubscribe from the live data of a stock.

```python
stocks_symbol = "SWIGGY"
groww_feed.subscribe_stocks_live(stocks_symbol)
live = groww_feed.get_stocks_live(stocks_symbol)
print(live)
# Or to get just the LTP
print(groww_feed.get_stocks_ltp(stocks_symbol))
groww_feed.unsubscribe_stocks_live(stocks_symbol)
```

##### Stocks Live Data - Request Fields

- `subscription_key` (str): The subscription key.

##### Stocks Live Data - Response Fields

Returns an Optional[[LivePriceData](#livepricedata)] which contains the live price data.

### Market Depth

#### Derivatives Market Depth

Subscribe to, get, and unsubscribe from the market depth of a derivatives contract.

```python
groww_feed.subscribe_derivatives_market_depth(derivatives_symbol)
market_depth = groww_feed.get_derivatives_market_depth(derivatives_symbol)
print(market_depth)
groww_feed.unsubscribe_derivatives_market_depth(derivatives_symbol)
```

#### Stocks Market Depth

Subscribe to, get, and unsubscribe from the market depth of a stock.

```python
groww_feed.subscribe_stocks_market_depth(stocks_symbol)
market_depth = groww_feed.get_stocks_market_depth(stocks_symbol)
print(market_depth)
groww_feed.unsubscribe_stocks_market_depth(stocks_symbol)
```

#### Market Depth - Request Fields

- `subscription_key` (str): The subscription key.

#### Market Depth - Response Fields

Returns an Optional[[MarketDepthData](#marketdepthdata)] which contains the market depth information.

### Market Info

Subscribe to, get, and unsubscribe from market information.

```python
groww_feed.subscribe_market_info()
market_info = groww_feed.get_market_info()
print(market_info)
groww_feed.unsubscribe_market_info()
```

#### Market Info - Response Fields

Returns an Optional[string] which contains the market information or status. Eg. MARKET_OPEN.

### Order Updates

#### Derivatives Order Updates

Subscribe to, get, and unsubscribe from order updates for a derivatives contract.

```python
user_id = "user123"
groww_feed.subscribe_derivatives_order_updates(user_id)
order_details = groww_feed.get_derivatives_order_update(user_id)
print(order_details)
groww_feed.unsubscribe_derivatives_order_updates(user_id)
```

#### Stocks Order Updates

Subscribe to, get, and unsubscribe from order updates for a user.

```python
user_id = "user123"
groww_feed.subscribe_stocks_order_updates(user_id)
order_details = groww_feed.get_stocks_order_update(user_id)
print(order_details)
groww_feed.unsubscribe_stocks_order_updates(user_id)
```

#### Order Updates - Request Fields

- `subscription_key` (str): The subscription key.

#### Order Updates - Response Fields

Returns an Optional[[OrderDetailDto](#orderdetaildto)] which contains the order details.

### Position Updates

Subscribe to, get, and unsubscribe from position updates for a user.

```python
groww_feed.subscribe_stocks_position_updates(user_id)
exchange_positions = groww_feed.get_stocks_position_update(user_id)
print(exchange_positions)
groww_feed.unsubscribe_stocks_position_updates(user_id)
```

#### Position Updates - Request Fields

- `subscription_key` (str): The subscription key.

#### Position Updates - Response Fields

Returns an Optional[[ExchangePosition](#exchangeposition)] which contains the exchange-wise position details.

## Enums

The SDK uses several enums to represent various trading parameters. The enums are located in `gwapex_base.groww.enums` module.

Below are the enums and their possible values:

### AmoStatus

Represents the status of a After Market Order (AMO) in the trading system.

- `NA`: Status not available
- `PENDING`: Order is pending for execution
- `DISPATCHED`: Order has been dispatched for execution
- `PARKED`: Order is parked for later execution
- `PLACED`: Order has been placed in the market
- `FAILED`: Order execution has failed
- `MARKET`: Order is a market order

### Validity

Specifies how long an order remains active in the trading system before it is automatically cancelled if not executed.

- `DAY`: Valid until market close on the same trading day
- `EOS`: End of Session - Valid until the end of current trading session
- `IOC`: Immediate or Cancel - Must be filled immediately (fully/partially) or cancelled
- `GTC`: Good Till Cancelled - Remains active until explicitly cancelled by trader
- `GTD`: Good Till Date - Valid until a specific date set by trader

### EquityType

Represents the type of equity instrument being traded, such as stocks, futures, options, etc.

- `STOCKS`: Regular equity shares of a company
- `FUTURE`: Derivatives contract to buy/sell an asset at a future date
- `OPTION`: Derivatives contract giving the right to buy/sell an asset at a future date
- `ETF`: Exchange Traded Fund - Basket of securities traded on an exchange
- `INDEX`: Composite value of a group of stocks representing a market
- `BONDS`: Debt instrument issued by a government or corporation

### Exchange

Represents the stock exchanges where the trades can be executed.

- `BSE`: Bombay Stock Exchange - Asia's oldest exchange, known for SENSEX index
- `MCX`: Multi Commodity Exchange - Leading commodity exchange in India
- `MCXSX`: MCX Stock Exchange - Former stock exchange in India
- `NCDEX`: National Commodity and Derivatives Exchange - Leading agri-commodity exchange
- `NSE`: National Stock Exchange - India's largest exchange by trading volume
- `US`: United States Stock Exchange

### OrderStatus

Represents the status of an order in the trading system.

- `NEW`: Order is newly created and pending for further processing
- `ACKED`: Order has been acknowledged by the system
- `TRIGGER_PENDING`: Order is waiting for a trigger event to be executed
- `APPROVED`: Order has been approved and is ready for execution
- `REJECTED`: Order has been rejected by the system
- `FAILED`: Order execution has failed
- `EXECUTED`: Order has been successfully executed
- `DELIVERY_AWAITED`: Order has been executed and waiting for delivery
- `CANCELLED`: Order has been cancelled
- `CANCELLATION_REQUESTED`: Request to cancel the order has been initiated
- `MODIFICATION_REQUESTED`: Request to modify the order has been initiated
- `COMPLETED`: Order has been completed

### OrderType

Defines how the order will be executed in terms of price. Different order types offer varying levels of price control and execution certainty.

- `LIMIT`: Specify exact price, may not get filled immediately but ensures price control
- `MARKET`: Immediate execution at best available price, no price guarantee
- `STOP_LOSS`: Protection order that triggers at specified price to limit losses
- `STOP_LOSS_MARKET`: Stop Loss Market - Market order triggered at specified price to limit losses

### Product

Specifies the trading product type which determines factors like leverage, holding period, margin requirements, and settlement rules.

- `ARBITRAGE`: For exploiting price differences between markets, requires quick execution
- `BO`: Bracket Order - Set target and stop-loss in a single order for risk management
- `CNC`: Cash and Carry - For delivery-based equity trading with full upfront payment
- `CO`: Cover Order - Intraday trading with built-in stop-loss for risk protection
- `NORMAL_MARGIN`: Regular margin trading allowing overnight positions with standard leverage
- `MIS`: Margin Intraday Square-off - Higher leverage but must close by day end
- `MTF`: Margin Trading Facility - Allows borrowing funds for delivery trading

### Segment

Defines the market segment which determines the type of instruments that can be traded and their associated rules and regulations.

- `CASH`: Regular equity market for trading stocks with delivery option
- `COMMODITY`: Commodity segment for trading physical commodities and derivatives
- `CURRENCY`: Currency segment for trading forex pairs and currency derivatives
- `DERIVATIVE`: Futures and Options segment for trading derivatives contracts

### TransactionType

Indicates whether the trader is entering a long position (buying) or short position (selling). Determines the direction of the trade and potential profit/loss scenarios.

- `BUY`: Long position - Profit from price increase, loss from price decrease
- `SELL`: Short position - Profit from price decrease, loss from price increase

## Models

The SDK uses several models to represent various trading data. Below are the models and their fields:

### ExchangePosition

Represents the exchange-wise position details.

- `symbolIsin` (Optional[str]): The ISIN of the symbol.
- `exchangePosition` (dict[str, [PositionDetailDto](#positiondetaildto)]): A dictionary of exchange-wise positions.

### Holding

Represents a holding.

- `activeDematTransferQty` (Optional[int]): Active demat transfer quantity.
- `avgPrice` (Optional[int]): Average price.
- `caAdditionalQty` (Optional[int]): Corporate action additional quantity.
- `dematFreeQty` (Optional[float]): Demat free quantity.
- `dematLockedQty` (Optional[float]): Demat locked quantity.
- `growwLockedQty` (Optional[float]): Groww locked quantity.
- `netQty` (Optional[float]): Net quantity.
- `pledgeQty` (Optional[float]): Pledge quantity.
- `repledgeQty` (Optional[float]): Repledge quantity.
- `symbolIsin` (Optional[str]): Symbol ISIN.
- `t1Qty` (Optional[float]): T1 quantity.

### LiveIndexData

Represents live index data.

- `close` (Optional[float]): The closing price of the index.
- `dayChange` (Optional[float]): The change in the index value for the day.
- `dayChangePerc` (Optional[float]): The percentage change in the index value for the day.
- `high` (Optional[float]): The highest price of the index for the day.
- `low` (Optional[float]): The lowest price of the index for the day.
- `open` (Optional[float]): The opening price of the index.
- `value` (Optional[float]): The current value of the index.
- `week52High` (Optional[float]): The 52-week high value of the index.
- `week52Low` (Optional[float]): The 52-week low value of the index.

### LivePriceData

Represents live price data.

- `avgPrice` (Optional[float]): The average price.
- `bidQty` (Optional[int]): The bid quantity.
- `bidPrice` (Optional[float]): The bid price.
- `close` (Optional[float]): The closing price.
- `dayChange` (Optional[float]): The change in price for the day.
- `dayChangePerc` (Optional[float]): The percentage change in price for the day.
- `high` (Optional[float]): The highest price for the day.
- `highPriceRange` (Optional[float]): The high price range.
- `highTradeRange` (Optional[float]): The high trade range.
- `impliedVolatility` (Optional[float]): The implied volatility.
- `lastTradeQty` (Optional[int]): The quantity of the last trade.
- `lastTradeTime` (Optional[int]): The time of the last trade.
- `low` (Optional[float]): The lowest price for the day.
- `lowPriceRange` (Optional[float]): The low price range.
- `lowTradeRange` (Optional[float]): The low trade range.
- `ltp` (Optional[float]): The last traded price.
- `marketCap` (Optional[float]): The market capitalization.
- `offerPrice` (Optional[float]): The offer price.
- `offerQty` (Optional[int]): The offer quantity.
- `oiDayChange` (Optional[float]): The change in open interest for the day.
- `oiDayChangePerc` (Optional[float]): The percentage change in open interest for the day.
- `open` (Optional[float]): The opening price.
- `openInterest` (Optional[float]): The open interest.
- `prevOpenInterest` (Optional[float]): The previous open interest.
- `totalBuyQty` (Optional[float]): The total buy quantity.
- `totalSellQty` (Optional[float]): The total sell quantity.
- `volume` (Optional[int]): The trading volume.
- `week52High` (Optional[float]): The 52-week high price.
- `week52Low` (Optional[float]): The 52-week low price.

### MarketDepthData

Represents the market depth information which includes the buy and sell orders at different price levels.

- `buyBook` (Optional[dict[int, dict]]): Aggregated buy orders showing demand with the different price levels as keys.
  - `price` (Optional[float]): The price.
  - `quantity` (Optional[int]): The quantity.
- `sellBook` (Optional[dict[int, dict]]): Aggregated sell orders showing supply with the different price levels as keys.
  - `price` (Optional[float]): The price.
  - `quantity` (Optional[int]): The quantity.

### LtpData

Represents the Last traded price of an instrument.

- `ltp` (Optional[float]): The price.

### IndexLtpData

Represents the Last traded price of an index.

- `ltp` (Optional[float]): The price.

### Trade

Represents a trade.

- `transaction_type` (Optional[str]): Buy/Sell indicator.
- `created_at` (Optional[datetime]): Creation time.
- `exchange` (Optional[str): Exchange.
- `exchange_order_id` (Optional[str]): Exchange order ID.
- `exchange_trade_id` (Optional[str]): Exchange trade ID.
- `exchange_update_time` (Optional[datetime]): Exchange update time.
- `groww_order_id` (Optional[str]): Groww order ID.
- `groww_trade_id` (Optional[str]): Groww trade ID.
- `nest_update_micros` (Optional[int]): Nest update micros.
- `nest_update_time` (Optional[datetime]): Nest update time.
- `price` (Optional[int]): Price.
- `product` (Optional[str]): Product.
- `qty` (Optional[int]): Quantity.
- `remark` (Optional[str]): Remark.
- `segment` (Optional[Segment]): Segment.
- `settlement_number` (Optional[str]): Settlement number.
- `symbol` (Optional[str]): Symbol.
- `trade_date_time` (Optional[datetime]): Trade date and time.
- `trade_status` (Optional[str]): Trade status.

### OrderDetailDto

- `amoStatus` (Optional[[AmoStatus](#amostatus)]): The status of an After Market Order (AMO).
- `avgFillPrice` (Optional[int]): The average fill price of the order.
- `buySell` (Optional[[TransactionType](#transactiontype)]): The type of transaction. The buy/sell indicator.
- `createdAt` (Optional[datetime]): The creation time.
- `deliverableQty` (Optional[int]): The deliverable quantity.
- `validity` (str): The duration of the order.
- `equityType` (str): The type of equity instrument.
- `exchangeTime` (Optional[datetime]): The exchange time.
- `exchange` (str): The exchange where the order is placed.
- `filledQty` (Optional[int]): The filled quantity of the order.
- `growwOrderId` (str): The Groww order ID.
- `orderReferenceId` (Optional[str]): The order reference ID.
- `orderStatus` (str): The status of the order.
- `orderType` (str): The type of the order.
- `price` (Optional[int]): The price of the order.
- `product` (str): The product type of the order.
- `quantity` (int): The quantity of the order.
- `remainingQuantity` (Optional[int]): The remaining quantity.
- `remark` (Optional[str]): Any remarks for the order.
- `segment` (str): The segment of the order.
- `symbol` (str): The symbol of the order.
- `tradeDate` (Optional[datetime]): The trade date.
- `triggerPrice` (Optional[int]): The trigger price.

### PositionDetailDto

Represents a position detail.

- `creditQuantity` (Optional[int]): Credit quantity.
- `creditPrice` (Optional[int]): Credit price.
- `debitQuantity` (Optional[int]): Debit quantity.
- `debitPrice` (Optional[int]): Debit price.
- `cfCreditQuantity` (Optional[int]): Carry forward credit quantity.
- `cfCreditPrice` (Optional[int]): Carry forward credit price.
- `cfDebitQuantity` (Optional[int]): Carry forward debit quantity.
- `cfDebitPrice` (Optional[int]): Carry forward debit price.
- `isValid` (Optional[bool]): Whether the position is valid.

## Possible Exceptions

The SDK provides custom exceptions to handle various error scenarios. These exceptions are located in the `gwapex_base.groww.exceptions` module.

Below are the custom exceptions and their business context:

### GrowwBaseException

This is the base class for all exceptions in the Groww SDK. It captures the general error message.

Expect this exception as a generic catch-all for errors that do not fall into more specific categories.

**Attributes:**

- `msg` (str): The error message associated with the exception.

### GrowwAPIException

This exception is raised for client-related errors, such as invalid requests or authentication failures.

Expect this exception to handle errors related to client-side issues, such as invalid API keys or malformed requests.

**Attributes:**

- `msg` (str): The error message.
- `code` (str): The error code.

### GrowwAPITimeoutException

This exception is raised when a request to the Groww API times out.

Expect this exception to handle scenarios where the API request takes too long to respond, indicating potential network issues or server overload.

**Attributes:**

- `msg` (str): The error message.

### GrowwFeedException

This exception is raised for errors related to the Groww feed.

Expect this exception to handle errors related to the feed, such as connection issues or subscription failures.

**Attributes:**

- `msg` (str): The error message.

### GrowwFeedConnectionException

This exception is raised when a connection to the Groww feed fails.

Expect this exception to handle errors related to establishing or maintaining a connection to the Groww feed, which is crucial for receiving live market data and updates.

**Attributes:**

- `msg` (str): The error message.

### GrowwFeedNotSubscribedException

This exception is raised when trying to access data from a feed that has not been subscribed to. A subscription is required to receive data from the feed.

Expect this exception to handle scenarios where the SDK attempts to retrieve data from a feed that has not been subscribed to, indicating a logical error in the code.

**Attributes:**

- `msg` (str): The error message.
- `topic` (str): The topic that must be subscribed to receive messages.
