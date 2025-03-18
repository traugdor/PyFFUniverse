import io
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from PIL import Image, ImageTk
from scipy.signal import find_peaks
import datetime
from datetime import datetime, timedelta
# Note: sklearn is installed as scikit-learn, but
# the import name is still 'sklearn'
from sklearn.linear_model import LinearRegression
from utils.translations import get_text
import matplotlib.gridspec as gridspec
import matplotlib.ticker as ticker

def create_price_history_graph(history_data, time_range, show_peaks=True, show_trend=True, show_avg=True):
    """
    Create a price history graph using matplotlib.
    
    Args:
        history_data (dict): The price history data from the Universalis API
        time_range (str): The time range to display (e.g. "7 Days")
        show_peaks (bool, optional): Whether to show peaks and valleys. Defaults to True.
        show_trend (bool, optional): Whether to show trend lines. Defaults to True.
        show_avg (bool, optional): Whether to show average price. Defaults to True.
        
    Returns:
        tuple: (PhotoImage, dict) The graph image as a PhotoImage and a dictionary with data point information
    """
    # Extract price history data
    timestamps = []
    prices = []
    quantities = []
    worlds = []
    
    # Get the time range in days
    days = get_time_range_days(time_range)
    
    # Calculate the cutoff date for filtering (if days > 0)
    cutoff_date = None
    if days > 0:
        cutoff_date = datetime.now() - timedelta(days=days)
    
    # Check different possible formats from the API
    if "entries" in history_data:
        entries = history_data["entries"]
        for entry in entries:
            if "pricePerUnit" in entry and "timestamp" in entry:
                # Convert timestamp to datetime
                if isinstance(entry["timestamp"], int):
                    # Convert from milliseconds to seconds if needed
                    if entry["timestamp"] > 1000000000000:  # If timestamp is in milliseconds
                        entry["timestamp"] = entry["timestamp"] / 1000
                    timestamp = datetime.fromtimestamp(entry["timestamp"])
                else:
                    # Try to parse as ISO format
                    try:
                        timestamp = datetime.fromisoformat(entry["timestamp"].replace('Z', '+00:00'))
                    except:
                        continue
                
                # Skip entries outside the time range
                if cutoff_date and timestamp < cutoff_date:
                    continue
                        
                timestamps.append(timestamp)
                prices.append(entry["pricePerUnit"])
                quantities.append(entry.get("quantity", 1))
                worlds.append(entry.get("worldName", ""))
    elif "sales" in history_data:
        sales = history_data["sales"]
        for sale in sales:
            if "pricePerUnit" in sale and "timestamp" in sale:
                # Convert timestamp to datetime
                if isinstance(sale["timestamp"], int):
                    # Convert from milliseconds to seconds if needed
                    if sale["timestamp"] > 1000000000000:  # If timestamp is in milliseconds
                        sale["timestamp"] = sale["timestamp"] / 1000
                    timestamp = datetime.fromtimestamp(sale["timestamp"])
                else:
                    # Try to parse as ISO format
                    try:
                        timestamp = datetime.fromisoformat(sale["timestamp"].replace('Z', '+00:00'))
                    except:
                        continue
                
                # Skip entries outside the time range
                if cutoff_date and timestamp < cutoff_date:
                    continue
                        
                timestamps.append(timestamp)
                prices.append(sale["pricePerUnit"])
                quantities.append(sale.get("quantity", 1))
                worlds.append(sale.get("worldName", ""))
    elif "recentHistory" in history_data:
        recent_history = history_data["recentHistory"]
        for history in recent_history:
            if "pricePerUnit" in history and "timestamp" in history:
                # Convert timestamp to datetime
                if isinstance(history["timestamp"], int):
                    # Convert from milliseconds to seconds if needed
                    if history["timestamp"] > 1000000000000:  # If timestamp is in milliseconds
                        history["timestamp"] = history["timestamp"] / 1000
                    timestamp = datetime.fromtimestamp(history["timestamp"])
                else:
                    # Try to parse as ISO format
                    try:
                        timestamp = datetime.fromisoformat(history["timestamp"].replace('Z', '+00:00'))
                    except:
                        continue
                
                # Skip entries outside the time range
                if cutoff_date and timestamp < cutoff_date:
                    continue
                        
                timestamps.append(timestamp)
                prices.append(history["pricePerUnit"])
                quantities.append(history.get("quantity", 1))
                worlds.append(history.get("worldName", ""))

    # If no data, return empty graph
    if not timestamps:
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.text(0.5, 0.5, get_text("market.no_listings", "No price history data available"), 
                horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)
        ax.set_xlabel(get_text("market.date", "Date"))
        ax.set_ylabel(get_text("market.price", "Price"))
        ax.set_title(get_text("market.price_history", "Price History"))
        
        # Convert to PhotoImage
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        img = Image.open(buf)
        img_tk = ImageTk.PhotoImage(img)
        plt.close()
        
        return img_tk, {}
    
    # Create figure with a special layout for side legend and predictions
    fig = plt.figure(figsize=(10, 6))
    
    # Create a gridspec layout with 1 row and 2 columns
    # The left column (for the main plot) will be wider than the right column (for legend and predictions)
    gs = gridspec.GridSpec(1, 2, width_ratios=[3, 1])
    
    # Create the main plot in the left column
    ax = fig.add_subplot(gs[0, 0])
    
    # Create the legend/info area in the right column
    info_ax = fig.add_subplot(gs[0, 1])
    info_ax.axis('off')  # Turn off axis for the info area
    
    # Sort data by timestamp
    sorted_data = sorted(zip(timestamps, prices, quantities, worlds), key=lambda x: x[0])
    timestamps, prices, quantities, worlds = zip(*sorted_data) if sorted_data else ([], [], [], [])
    
    # Create a list to track data points for tooltip functionality
    data_points = []
    
    # Create scatter plot with lines
    scatter = ax.scatter(timestamps, prices, s=40, alpha=0.7, picker=5, color='blue')
    ax.plot(timestamps, prices, '-', color='blue', alpha=0.5, linewidth=1.5)
    
    # Store the data points for tooltip functionality
    for i in range(len(timestamps)):
        data_points.append({
            'timestamp': timestamps[i],
            'price': prices[i],
            'quantity': quantities[i],
            'world': worlds[i] if i < len(worlds) else ""
        })
    
    # Show average price if requested
    if show_avg and len(prices) > 0:
        avg_price = sum(prices) / len(prices)
        ax.axhline(y=avg_price, color='blue', linestyle='--', alpha=0.7, 
                   label=get_text("market.avg_price", "Average Price"))
    
    # Show trend lines for peaks and valleys if requested
    if show_trend and len(timestamps) > 1:
        try:
            # Calculate average price
            avg_price = sum(prices) / len(prices)
            
            # Separate data points above and below average
            above_avg_timestamps = []
            above_avg_prices = []
            below_avg_timestamps = []
            below_avg_prices = []
            
            for i, price in enumerate(prices):
                if price >= avg_price:
                    above_avg_timestamps.append(timestamps[i])
                    above_avg_prices.append(price)
                else:
                    below_avg_timestamps.append(timestamps[i])
                    below_avg_prices.append(price)
            
            # Convert datetime to numeric for regression
            x_above = mdates.date2num(above_avg_timestamps)
            x_below = mdates.date2num(below_avg_timestamps)
            
            # Only proceed if we have enough data points
            if len(x_above) > 1:
                # Reshape for sklearn
                X_above = x_above.reshape(-1, 1)
                y_above = np.array(above_avg_prices)
                
                # Fit linear regression for peaks
                model_above = LinearRegression()
                model_above.fit(X_above, y_above)
                
                # Generate trend line points
                x_above_trend = np.linspace(min(x_above), max(x_above), 100)
                y_above_trend = model_above.predict(x_above_trend.reshape(-1, 1))
                
                # Convert back to datetime for plotting
                x_above_trend_dates = mdates.num2date(x_above_trend)
                
                # Plot trend line for peaks
                ax.plot(x_above_trend_dates, y_above_trend, 'r-', linewidth=2, label=get_text("market.peak_trend", "Peak Trend"))
                
                # Extend trend line for prediction (1 day into the future)
                last_date = max(timestamps)
                future_date = last_date + timedelta(days=1)
                x_peak_trend = np.linspace(min(x_above), mdates.date2num(future_date), 100)
                y_peak_trend = model_above.predict(x_peak_trend.reshape(-1, 1))
                x_peak_trend_dates = mdates.num2date(x_peak_trend)
            
            if len(x_below) > 1:
                # Reshape for sklearn
                X_below = x_below.reshape(-1, 1)
                y_below = np.array(below_avg_prices)
                
                # Fit linear regression for valleys
                model_below = LinearRegression()
                model_below.fit(X_below, y_below)
                
                # Generate trend line points
                x_below_trend = np.linspace(min(x_below), max(x_below), 100)
                y_below_trend = model_below.predict(x_below_trend.reshape(-1, 1))
                
                # Convert back to datetime for plotting
                x_below_trend_dates = mdates.num2date(x_below_trend)
                
                # Plot trend line for valleys
                ax.plot(x_below_trend_dates, y_below_trend, 'g-', linewidth=2, label=get_text("market.valley_trend", "Valley Trend"))
                
                # Extend trend line for prediction (1 day into the future)
                last_date = max(timestamps)
                future_date = last_date + timedelta(days=1)
                x_valley_trend = np.linspace(min(x_below), mdates.date2num(future_date), 100)
                y_valley_trend = model_below.predict(x_valley_trend.reshape(-1, 1))
                x_valley_trend_dates = mdates.num2date(x_valley_trend)
                
            # Highlight the prediction part with a different color/style
            if 'x_peak_trend' in locals() and 'y_peak_trend' in locals():
                prediction_start_idx = np.argmax(x_peak_trend >= mdates.date2num(last_date))
                if prediction_start_idx < len(x_peak_trend_dates):
                    # Use a more distinct color (magenta) for peak predictions
                    ax.plot(x_peak_trend_dates[prediction_start_idx:], y_peak_trend[prediction_start_idx:], 
                            color='magenta', linestyle='--', linewidth=2.5, 
                            label=get_text("market.peak_prediction", "Peak Prediction"))
                
            if 'x_valley_trend' in locals() and 'y_valley_trend' in locals():
                prediction_start_idx = np.argmax(x_valley_trend >= mdates.date2num(last_date))
                if prediction_start_idx < len(x_valley_trend_dates):
                    # Use a more distinct color (cyan) for valley predictions
                    ax.plot(x_valley_trend_dates[prediction_start_idx:], y_valley_trend[prediction_start_idx:], 
                            color='cyan', linestyle='--', linewidth=2.5, 
                            label=get_text("market.valley_prediction", "Valley Prediction"))
        except Exception as e:
            print(f"Error calculating trend lines: {e}")
    
    # Add tomorrow's price prediction text to the info area instead of on the main plot
    prediction_text = ""
    try:
        if show_trend and 'x_peak_trend' in locals() and 'y_peak_trend' in locals() and 'x_valley_trend' in locals() and 'y_valley_trend' in locals():
            # Get tomorrow's date
            last_date = max(timestamps)
            tomorrow = last_date + timedelta(days=1)
            tomorrow_str = tomorrow.strftime('%Y-%m-%d')
            
            # Create prediction text
            prediction_text = get_text("market.tomorrow_prediction", "Tomorrow's Price Prediction ({date}):\n").format(date=tomorrow_str)
            
            # Get peak prediction if available
            try:
                if 'model_above' in locals():
                    peak_prediction = model_above.predict([[mdates.date2num(tomorrow)]])[0]
                    peak_prediction_rounded = round(peak_prediction, 2)
                    prediction_text += get_text("market.peak_price", "Peak Price: {price}\n").format(price=peak_prediction_rounded)
            except Exception as e:
                pass
            
            # Get valley prediction if available
            try:
                if 'model_below' in locals():
                    valley_prediction = model_below.predict([[mdates.date2num(tomorrow)]])[0]
                    valley_prediction_rounded = round(valley_prediction, 2)
                    prediction_text += get_text("market.valley_price", "Valley Price: {price}\n").format(price=valley_prediction_rounded)
            except Exception as e:
                pass
            
            # Calculate average price prediction if we have both peak and valley
            try:
                if 'peak_prediction' in locals() and 'valley_prediction' in locals():
                    avg_prediction = (peak_prediction + valley_prediction) / 2
                    avg_prediction_rounded = round(avg_prediction, 2)
                    prediction_text += get_text("market.average_price", "Average Price: {price}").format(price=avg_prediction_rounded)
            except Exception as e:
                pass
    except Exception as e:
        print(f"Error calculating tomorrow's price prediction: {e}")
    
    # Format the x-axis to show dates nicely
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    plt.xticks(rotation=45)
    
    # Add labels and title
    ax.set_xlabel(get_text("market.date", "Date"))
    ax.set_ylabel(get_text("market.price", "Price"))
    ax.set_title(get_text("market.price_history", "Price History"))
    
    # Add grid for better readability
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Get the legend handles and labels from the main plot
    handles, labels = ax.get_legend_handles_labels()
    
    # Add the legend to the info area instead of the main plot
    if handles:
        info_ax.legend(handles, labels, loc='upper center', fontsize=10)
    
    # Add the prediction text to the info area if available
    if prediction_text:
        info_ax.text(0.05, 0.5, prediction_text, fontsize=10, verticalalignment='center')
    
    # Adjust layout to make room for the rotated x-axis labels
    plt.tight_layout()
    
    # Get figure dimensions and data point coordinates
    fig_width, fig_height = fig.get_size_inches() * fig.dpi
    
    # Get the main plot area coordinates in figure space
    bbox = ax.get_position()
    plot_area = {
        'x0': bbox.x0,
        'y0': bbox.y0,
        'x1': bbox.x1,
        'y1': bbox.y1
    }
    
    # Convert to PhotoImage
    buf = io.BytesIO()
    plt.savefig(buf, format='png', dpi=100)
    buf.seek(0)
    img = Image.open(buf)
    img_tk = ImageTk.PhotoImage(img)
    plt.close()
    
    # Return the image and the data point information
    return img_tk, {'data_points': data_points, 'plot_area': plot_area}

def get_time_range_days(time_range_text):
    """
    Convert a time range text to number of days.
    
    Args:
        time_range_text (str): The time range text (e.g., "7 Days")
        
    Returns:
        int: Number of days, or 0 for "All Time"
    """
    # Get the English versions of the time range texts for comparison
    time_24h = get_text("market.24_hours", "24 Hours")
    time_7d = get_text("market.7_days", "7 Days")
    time_30d = get_text("market.30_days", "30 Days")
    time_90d = get_text("market.90_days", "90 Days")
    time_all = get_text("market.all_time", "All Time")
    
    if time_range_text == time_24h:
        return 1
    elif time_range_text == time_7d:
        return 7
    elif time_range_text == time_30d:
        return 30
    elif time_range_text == time_90d:
        return 90
    elif time_range_text == time_all:
        return 0  # 0 means all time
    else:
        return 7  # Default to 7 days
