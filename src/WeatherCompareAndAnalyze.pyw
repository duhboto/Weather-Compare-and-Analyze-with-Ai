import time
import tkinter as tk
import webbrowser
from tkinter import messagebox, scrolledtext
import requests
import json
import geocoder
import matplotlib.pyplot as plt
import csv
import os
from datetime import datetime
import keyring
import openai
import threading

class WeatherApp:
    def __init__(self, root):
        self.root = root
        self.root.geometry('1050x1200')
        self.root.title('Weather App')
        # Defining tkinter variables
        self.location_var1 = tk.StringVar()
        self.location_var2 = tk.StringVar()
        self.api_key_var = tk.StringVar()
        self.openai_api_key_var = tk.StringVar()
        self.temperature_unit_var = tk.StringVar(value='C')
        self.analysis_checkbox_var = tk.IntVar()

        # Creating Widgets
        self.create_widgets()

        # Weather data for comparison
        self.weather_data1 = {}
        self.weather_data2 = {}

        # Check if API keys are stored and load them if available
        if keyring.get_password('weather_app', 'api_key'):
            self.api_key_var.set(keyring.get_password('weather_app', 'api_key'))
        else:
            self.api_key_var.set("")  # Set the API key variable to an empty string

        if keyring.get_password('weather_app', 'openai_api_key'):
            self.openai_api_key_var.set(keyring.get_password('weather_app', 'openai_api_key'))
            openai.api_key = self.openai_api_key_var.get()  # Set OpenAI API key
        else:
            self.openai_api_key_var.set("")  # Set the OpenAI API key variable to an empty string


    def create_widgets(self):
        # Location Entry and Button
        location_label1 = tk.Label(self.root, text='Location 1:')
        location_label1.grid(row=0, column=0, sticky='w')

        location_entry1 = tk.Entry(self.root, textvariable=self.location_var1)
        location_entry1.grid(row=0, column=1, pady=5)

        location_label2 = tk.Label(self.root, text='Location 2:')
        location_label2.grid(row=1, column=0, sticky='w')

        location_entry2 = tk.Entry(self.root, textvariable=self.location_var2)
        location_entry2.grid(row=1, column=1, pady=5)

        # API Key Entry and API Website Label
        if not self.api_key_var.get():
            api_key_label = tk.Label(self.root, text='API Key:')
            api_key_label.grid(row=2, column=0, sticky='w')

            api_key_entry = tk.Entry(self.root, show='*', textvariable=self.api_key_var)
            api_key_entry.grid(row=2, column=1)

            save_api_key_button = tk.Button(self.root, text='Save API Key', command=self.save_api_key)
            save_api_key_button.grid(row=2, pady=10, column=2)
        else:
            api_website_label = tk.Label(self.root, text='API Key:')
            api_website_label.grid(row=2, column=0, sticky='w')

            api_key_display = tk.Label(self.root, text='******', font=('Helvetica', 10))
            api_key_display.grid(row=2, column=1)

        # OpenAI API Key Entry
        openai_api_key_label = tk.Label(self.root, text='OpenAI API Key:')
        openai_api_key_label.grid(row=3, column=0, sticky='w')

        openai_api_key_entry = tk.Entry(self.root, show='*', textvariable=self.openai_api_key_var)
        openai_api_key_entry.grid(row=3, column=1)

        save_openai_api_key_button = tk.Button(self.root, text='Save OpenAI API Key', command=self.save_openai_api_key)
        save_openai_api_key_button.grid(row=3, pady=10, column=2)

        api_website_label = tk.Label(self.root, text='API Website:')
        api_website_label.grid(row=4, column=0, sticky='w')

        api_website_link = tk.Label(self.root, text='http://api.openweathermap.org', fg='blue', cursor='hand2')
        api_website_link.grid(row=4, column=1, columnspan=2, sticky='w')
        api_website_link.bind('<Button-1>', lambda e: self.open_website('http://api.openweathermap.org'))

        openai_website_label = tk.Label(self.root, text='OpenAI API Website:')
        openai_website_label.grid(row=5, column=0, sticky='w')

        openai_website_link = tk.Label(self.root, text='https://openai.com/', fg='blue', cursor='hand2')
        openai_website_link.grid(row=5, column=1, columnspan=2, sticky='w')
        openai_website_link.bind('<Button-1>', lambda e: self.open_website('https://openai.com/'))

        # Button Frame
        button_frame = tk.Frame(self.root)
        button_frame.grid(row=6, column=0, columnspan=3, pady=10)

        get_weather_button = tk.Button(button_frame, text='Get Weather', command=self.get_weather)
        get_weather_button.pack(side=tk.LEFT, padx=5)

        detect_location_button = tk.Button(button_frame, text='Detect Location', command=self.detect_location)
        detect_location_button.pack(side=tk.LEFT, padx=5)

        compare_weather_button = tk.Button(button_frame, text='Compare Weather', command=self.compare_weather)
        compare_weather_button.pack(side=tk.LEFT, padx=5)

        # Analysis Checkbox
        analysis_checkbox = tk.Checkbutton(button_frame, text='Perform AI Summary', variable=self.analysis_checkbox_var)
        analysis_checkbox.pack(side=tk.LEFT, padx=5)

        # Temperature Unit Radio Buttons
        temperature_unit_frame = tk.Frame(self.root)
        temperature_unit_frame.grid(row=7, column=0, columnspan=3)

        temperature_unit_label = tk.Label(temperature_unit_frame, text='Temperature Unit:')
        temperature_unit_label.pack(side=tk.LEFT)

        celsius_radio_button = tk.Radiobutton(temperature_unit_frame, text='Celsius', variable=self.temperature_unit_var, value='C')
        celsius_radio_button.pack(side=tk.LEFT, padx=5)

        fahrenheit_radio_button = tk.Radiobutton(temperature_unit_frame, text='Fahrenheit', variable=self.temperature_unit_var, value='F')
        fahrenheit_radio_button.pack(side=tk.LEFT, padx=5)

        # Instructions Label
        instructions_label = tk.Label(self.root, text='Instructions:', font=('Helvetica', 12, 'bold'))
        instructions_label.grid(row=8, column=0, columnspan=3, pady=10)

        instructions_text = scrolledtext.ScrolledText(self.root, width=80, height=8)
        instructions_text.insert(tk.END, '1. Enter the locations for comparison in Location 1 and Location 2 fields.\n\n2. Provide the API Key and OpenAI API Key. If not available, click "Save API Key" and "Save OpenAI API Key" respectively.\n\n3. Use "Get Weather" button to fetch weather data for each location.\n\n4. "Detect Location" button automatically fills Location 1with the detected location based on your IP address.\n\n5. Click "Compare Weather" to compare the temperature and humidity between the two locations.\n\n6. To generate analysis, click "Start Generate Analysis". If selected, the AI summary and additional analysis will be displayed.\n\nNote: Please ensure the API keys are valid and you have an active internet connection.')
        instructions_text.configure(state='disabled')
        instructions_text.grid(row=9, column=0, columnspan=3, padx=10)

        # Analysis Frame
        analysis_frame = tk.Frame(self.root)
        analysis_frame.grid(row=0, column=3, rowspan=12, padx=10)

        # Analysis Summary Label
        summary_label = tk.Label(analysis_frame, text='Analysis Summary:', font=('Helvetica', 12, 'bold'))
        summary_label.pack(pady=10)

        # Analysis Summary Text
        self.summary_text = scrolledtext.ScrolledText(analysis_frame, width=40, height=10)
        self.summary_text.pack()

        # 7-Day Data Analysis Label
        analysis_label = tk.Label(analysis_frame, text='7-Day Data Analysis:', font=('Helvetica', 12, 'bold'))
        analysis_label.pack(pady=10)

        # 7-Day Data Analysis Text
        self.analysis_text = scrolledtext.ScrolledText(analysis_frame, width=40, height=20)
        self.analysis_text.pack()

        # Generate Analysis Button
        generate_analysis_button = tk.Button(analysis_frame, text='Start Generate Analysis', command=self.generate_analysis)
        generate_analysis_button.pack(pady=10)
        # Create Graphs Button
        create_graphs_button = tk.Button(analysis_frame, text='Create Graphs', command=self.create_graphs)
        create_graphs_button.pack(pady=10)


    def save_api_key(self):
        if self.api_key_var.get():
            keyring.set_password('weather_app', 'api_key', self.api_key_var.get())
            messagebox.showinfo('Success', 'API Key Saved Successfully')
        else:
            messagebox.showerror('Error', 'Please Enter API Key')

    def save_openai_api_key(self):
        if self.openai_api_key_var.get():
            keyring.set_password('weather_app', 'openai_api_key', self.openai_api_key_var.get())
            openai.api_key = self.openai_api_key_var.get()  # Set OpenAI API key
            messagebox.showinfo('Success', 'OpenAI API Key Saved Successfully')
        else:
            messagebox.showerror('Error', 'Please Enter OpenAI API Key')

    def get_weather(self):
        if not self.api_key_var.get():
            messagebox.showerror('Error', 'Please Enter API Key')
            return

        location1 = self.location_var1.get()
        location2 = self.location_var2.get()

        if location1:
            self.weather_data1 = self.fetch_weather_data(location1)
            self.display_weather_data(self.weather_data1, 13)
            self.get_forecast_data(location1, 19)
            self.get_historical_data(location1, 27)
            time.sleep(1)  # Add a delay of 1 second

        if location2:
            self.weather_data2 = self.fetch_weather_data(location2)
            self.display_weather_data(self.weather_data2, 37)
            self.get_forecast_data(location2, 43)
            self.get_historical_data(location2, 51)
            time.sleep(1)  # Add a delay of 1 second

    def fetch_weather_data(self, location):
        base_url = 'http://api.openweathermap.org/data/2.5/weather'
        params = {
            'q': location,
            'appid': keyring.get_password('weather_app', 'api_key'),
            'units': 'metric' if self.temperature_unit_var.get() == 'C' else 'imperial'
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        if response.status_code != 200:
            error_message = f"Error: {data.get('message', 'Unknown error')}"
            messagebox.showerror('Error', error_message)
            return {}

        if data.get('cod') != 200:
            error_message = f"Error: {data.get('message', 'Unknown error')}"
            messagebox.showerror('Error', error_message)
            return {}

        # Save weather data to a CSV file
        self.save_weather_data_to_csv(data, location)

        return data

    def get_forecast_data(self, location, row):
        base_url = 'http://api.openweathermap.org/data/2.5/forecast'
        params = {
            'q': location,
            'appid': keyring.get_password('weather_app', 'api_key'),
            'units': 'metric' if self.temperature_unit_var.get() == 'C' else 'imperial',
            'cnt': 7
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        if response.status_code != 200:
            error_message = f"Error: {data.get('message', 'Unknown error')}"
            messagebox.showerror('Error', error_message)
            return

        if data.get('cod') != '200':
            error_message = f"Error: {data.get('message', 'Unknown error')}"
            messagebox.showerror('Error', error_message)
            return

        forecast_label = tk.Label(self.root, text='7-Day Forecast:', font=('Helvetica', 12, 'bold'))
        forecast_label.grid(row=row, column=0, columnspan=3, pady=10)

        forecast_text = scrolledtext.ScrolledText(self.root, width=80, height=5)
        for forecast in data['list']:
            forecast_text.insert(tk.END, f"Date: {forecast['dt_txt']}\nTemperature: {forecast['main']['temp']}°{self.temperature_unit_var.get()}\nHumidity: {forecast['main']['humidity']}%\n\n")
        forecast_text.configure(state='disabled')
        forecast_text.grid(row=row+1, column=0, columnspan=3, padx=10)

    def get_historical_data(self, location, row):
        base_url = 'http://api.openweathermap.org/data/2.5/onecall/timemachine'
        params = {
            'lat': '',
            'lon': '',
            'appid': keyring.get_password('weather_app', 'api_key'),
            'units': 'metric' if self.temperature_unit_var.get() == 'C' else 'imperial',
            'dt': int(datetime.now().timestamp())
        }

        geocode_url = 'https://api.openweathermap.org/geo/1.0/direct'
        geocode_params = {
            'q': location,
            'limit': 1,
            'appid': keyring.get_password('weather_app', 'api_key')
        }
        geocode_response = requests.get(geocode_url, params=geocode_params)
        geocode_data = geocode_response.json()

        if geocode_response.status_code != 200:
            error_message = f"Error: {geocode_data.get('message', 'Unknown error')}"
            messagebox.showerror('Error', error_message)
            return

        if not geocode_data:
            messagebox.showerror('Error', 'Location not found')
            return

        params['lat'] = geocode_data[0]['lat']
        params['lon'] = geocode_data[0]['lon']

        response = requests.get(base_url, params=params)
        data = response.json()

        if response.status_code != 200:
            error_message = f"Error: {data.get('message', 'Unknown error')}"
            messagebox.showerror('Error', error_message)
            return

        if data.get('cod') != '200':
            error_message = f"Error: {data.get('message', 'Unknown error')}"
            messagebox.showerror('Error', error_message)
            return

        historical_label = tk.Label(self.root, text='Historical Data:', font=('Helvetica', 12, 'bold'))
        historical_label.grid(row=row, column=0, columnspan=3, pady=10)

        historical_text = scrolledtext.ScrolledText(self.root, width=80, height=5)
        for hourly in data['hourly']:
            historical_text.insert(tk.END, f"Time: {datetime.fromtimestamp(hourly['dt']).strftime('%Y-%m-%d %H:%M:%S')}\nTemperature: {hourly['temp']}°{self.temperature_unit_var.get()}\nHumidity: {hourly['humidity']}%\n\n")
        historical_text.configure(state='disabled')
        historical_text.grid(row=row+1, column=0, columnspan=3, padx=10)


    def display_weather_data(self, data, row):
        if data:
            location_label = tk.Label(self.root, text=f"Location: {data['name']}, {data['sys']['country']}")
            location_label.grid(row=row, column=0, columnspan=3)

            temperature_label = tk.Label(self.root, text=f"Temperature: {data['main']['temp']}°{self.temperature_unit_var.get()}")
            temperature_label.grid(row=row+1, column=0, columnspan=3)

            humidity_label = tk.Label(self.root, text=f"Humidity: {data['main']['humidity']}%")
            humidity_label.grid(row=row+2, column=0, columnspan=3)

            weather_label = tk.Label(self.root, text=f"Weather: {data['weather'][0]['main']}")
            weather_label.grid(row=row+3, column=0, columnspan=3)

    def get_forecast_data(self, location, row):
        base_url = 'http://api.openweathermap.org/data/2.5/forecast'
        params = {
            'q': location,
            'appid': keyring.get_password('weather_app', 'api_key'),
            'units': 'metric' if self.temperature_unit_var.get() == 'C' else 'imperial',
            'cnt': 7
        }
        response = requests.get(base_url, params=params)
        data = response.json()

        if data.get('cod') != '200':
            messagebox.showerror('Error', data.get('message'))
            return

        forecast_label = tk.Label(self.root, text='7-Day Forecast:', font=('Helvetica', 12, 'bold'))
        forecast_label.grid(row=row, column=0, columnspan=3, pady=10)

        forecast_text = scrolledtext.ScrolledText(self.root, width=80, height=5)
        for forecast in data['list']:
            forecast_text.insert(tk.END, f"Date: {forecast['dt_txt']}\nTemperature: {forecast['main']['temp']}°{self.temperature_unit_var.get()}\nHumidity: {forecast['main']['humidity']}%\n\n")
        forecast_text.configure(state='disabled')
        forecast_text.grid(row=row+1, column=0, columnspan=3, padx=10)

    def get_historical_data(self, location, row):
        base_url = 'http://api.openweathermap.org/data/2.5/onecall/timemachine'
        params = {
            'lat': '',
            'lon': '',
            'appid': keyring.get_password('weather_app', 'api_key'),
            'units': 'metric' if self.temperature_unit_var.get() == 'C' else 'imperial',
            'dt': int(datetime.now().timestamp())
        }

        geocode_url = 'https://api.openweathermap.org/geo/1.0/direct'
        geocode_params = {
            'q': location,
            'limit': 1,
            'appid': keyring.get_password('weather_app', 'api_key')
        }
        geocode_response = requests.get(geocode_url, params=geocode_params)
        geocode_data = geocode_response.json()

        if geocode_data:
            params['lat'] = geocode_data[0]['lat']
            params['lon'] = geocode_data[0]['lon']

        response = requests.get(base_url, params=params)
        data = response.json()

        if data.get('cod') != '200':
            messagebox.showerror('Error', data.get('message'))
            return

        historical_label = tk.Label(self.root, text='Historical Data:', font=('Helvetica', 12, 'bold'))
        historical_label.grid(row=row, column=0, columnspan=3, pady=10)

        historical_text = scrolledtext.ScrolledText(self.root, width=80, height=5)
        for hourly in data['hourly']:
            historical_text.insert(tk.END, f"Time: {datetime.fromtimestamp(hourly['dt']).strftime('%Y-%m-%d %H:%M:%S')}\nTemperature: {hourly['temp']}°{self.temperature_unit_var.get()}\nHumidity: {hourly['humidity']}%\n\n")
        historical_text.configure(state='disabled')
        historical_text.grid(row=row+1, column=0, columnspan=3, padx=10)

    def detect_location(self):
        g = geocoder.ip('me')
        self.location_var1.set(g.city)

    def compare_weather(self):
        if self.weather_data1 and self.weather_data2:
            temp_diff = abs(self.weather_data1['main']['temp'] - self.weather_data2['main']['temp'])
            humidity_diff = abs(self.weather_data1['main']['humidity'] - self.weather_data2['main']['humidity'])
            comparison_label = tk.Label(self.root, text=f"Temperature Difference: {temp_diff}°{self.temperature_unit_var.get()}, Humidity Difference: {humidity_diff}%")
            comparison_label.grid(row=56, column=0, columnspan=3)

    def generate_analysis(self):
        if self.weather_data1 and self.weather_data2:
            # Save weather data to CSV
            with open('weather_data.csv', 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([datetime.now(), self.weather_data1['name'], self.weather_data1['main']['temp'], self.weather_data1['main']['humidity']])
                writer.writerow([datetime.now(), self.weather_data2['name'], self.weather_data2['main']['temp'], self.weather_data2['main']['humidity']])

            # Generate summary
            self.analysis_indicator_label = tk.Label(self.root, text='Generating Analysis...', font=('Helvetica', 12, 'bold'))
            self.analysis_indicator_label.grid(row=57, column=0, columnspan=3, pady=10)

            summary_thread = threading.Thread(target=self.generate_summary)
            summary_thread.start()

            messagebox.showinfo('Success', 'Weather Data Saved Successfully')

    def generate_summary(self):
        # Generate summary using OpenAI API
        prompt = f"Weather Analysis:\n\nLocation 1: {self.weather_data1['name']}, {self.weather_data1['sys']['country']}\nTemperature: {self.weather_data1['main']['temp']}°{self.temperature_unit_var.get()}\nHumidity: {self.weather_data1['main']['humidity']}%\n\nLocation 2: {self.weather_data2['name']}, {self.weather_data2['sys']['country']}\nTemperature: {self.weather_data2['main']['temp']}°{self.temperature_unit_var.get()}\nHumidity: {self.weather_data2['main']['humidity']}%"

        response = openai.Completion.create(
            engine='text-davinci-003',
            prompt=prompt,
            max_tokens=100,
            temperature=0.7,
            n=1,
            stop=None,
        )

        summary = response.choices[0].text.strip()

        # Display summary in GUI
        self.summary_text.configure(state='normal')
        self.summary_text.delete('1.0', tk.END)
        self.summary_text.insert(tk.END, summary)
        self.summary_text.configure(state='disabled')

        # Perform ChatGPT analysis if checkbox is selected
        if self.analysis_checkbox_var.get() == 1:
            self.perform_chatgpt_analysis(summary)

        self.analysis_indicator_label.destroy()

    def perform_chatgpt_analysis(self, summary):
        # Generate additional prompt for 7-day data analysis
        prompt_7day = f"Be scientific and Look at the trends between these two weather patterns and perform an analysis of their differences, etc., and provide a summary. Do not repeat what is already in the summary.\n\nLocation 1: {self.weather_data1['name']}, {self.weather_data1['sys']['country']}\n7-Day Forecast: ...\n\nLocation 2: {self.weather_data2['name']}, {self.weather_data2['sys']['country']}\n7-Day Forecast: ..."

        # Combine the original summary prompt and the 7-day data prompt
        prompt_combined = f"{summary}\n\n{prompt_7day}"

        # Generate summary for the combined prompt using ChatGPT
        response_combined = openai.Completion.create(
            engine='text-davinci-003',
            prompt=prompt_combined,
            max_tokens=2000,
            temperature=0.7,
            n=2,  # Request 2 choices to ensure we have enough
            stop=None,
        )

        if len(response_combined.choices) >= 2:
            # Extract the original summary response and the 7-day data analysis response
            response_summary = response_combined.choices[0].text.strip()
            response_7day = response_combined.choices[1].text.strip()

            # Display the original summary in the GUI
            self.summary_text.configure(state='normal')
            self.summary_text.delete('1.0', tk.END)
            self.summary_text.insert(tk.END, response_summary)
            self.summary_text.configure(state='disabled')

            # Display the 7-day data analysis in the GUI
            self.analysis_text.configure(state='normal')
            self.analysis_text.delete('1.0', tk.END)
            self.analysis_text.insert(tk.END, response_7day)
            self.analysis_text.configure(state='disabled')
        else:
            messagebox.showerror('Error', 'Insufficient response choices. Please try again.')
    def create_graphs(self):
        if self.weather_data1 and self.weather_data2:
            # Get temperature and humidity data for each location
            location1 = self.weather_data1['name']
            temperature1 = self.weather_data1['main']['temp']
            humidity1 = self.weather_data1['main']['humidity']

            location2 = self.weather_data2['name']
            temperature2 = self.weather_data2['main']['temp']
            humidity2 = self.weather_data2['main']['humidity']

            # Create temperature comparison graph
            plt.figure(figsize=(10, 6))
            plt.title('Temperature Comparison')
            plt.xlabel('Location')
            plt.ylabel('Temperature (°C)')
            plt.bar([location1, location2], [temperature1, temperature2])
            plt.show()

            # Create humidity comparison graph
            plt.figure(figsize=(10, 6))
            plt.title('Humidity Comparison')
            plt.xlabel('Location')
            plt.ylabel('Humidity (%)')
            plt.bar([location1, location2], [humidity1, humidity2])
            plt.show()
        else:
            messagebox.showerror('Error', 'Weather data not available for both locations. Please fetch weather data first.')

    def save_weather_data_to_csv(self, data, location):
        filename = 'weather_data.csv'
        header = ['Timestamp', 'Location', 'Temperature (°C)', 'Humidity (%)']

        # Check if the file already exists
        file_exists = os.path.isfile(filename)

        with open(filename, 'a', newline='') as file:
            writer = csv.writer(file)

            if not file_exists:
                writer.writerow(header)

            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            temperature = data['main']['temp']
            humidity = data['main']['humidity']

            writer.writerow([timestamp, location, temperature, humidity])

    def open_website(self, url):
        webbrowser.open(url, new=1)

if __name__ == '__main__':
    root = tk.Tk()
    app = WeatherApp(root)
    root.mainloop()
