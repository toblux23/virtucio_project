import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
from datetime import datetime

class PaymentPopup:
    def __init__(self, parent, user_id, spot_id):
        self.top = tk.Toplevel(parent)
        self.top.title("Process Payment")
        self.top.geometry("400x300")
        
        self.top.transient(parent)
        self.top.grab_set()
        
        # Store reference to main window
        self.main_app = parent.master  # This gets the ParkingGUI instance
        
        # Payment frame
        payment_frame = ttk.LabelFrame(self.top, text="Payment Details")
        payment_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(payment_frame, text="User ID:").grid(row=0, column=0, padx=5, pady=5)
        self.user_id_var = tk.StringVar(value=user_id)
        ttk.Entry(payment_frame, textvariable=self.user_id_var, state='readonly').grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(payment_frame, text="Spot ID:").grid(row=1, column=0, padx=5, pady=5)
        self.spot_id_var = tk.StringVar(value=spot_id)
        ttk.Entry(payment_frame, textvariable=self.spot_id_var, state='readonly').grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(payment_frame, text="Amount:").grid(row=2, column=0, padx=5, pady=5)
        self.amount_var = tk.StringVar(value="10.00")  # Default amount
        ttk.Entry(payment_frame, textvariable=self.amount_var).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(payment_frame, text="Payment Type:").grid(row=3, column=0, padx=5, pady=5)
        self.payment_type_var = tk.StringVar()
        ttk.Combobox(payment_frame, textvariable=self.payment_type_var, 
                    values=["GCASH", "Maya", "Cash"]).grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Button(payment_frame, text="Process Payment", command=self.process_payment).grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(payment_frame, text="Cancel", command=self.cancel_reservation).grid(row=5, column=0, columnspan=2, pady=5)
    
    def process_payment(self):
        try:
            user_id = self.user_id_var.get()
            amount = self.amount_var.get()
            payment_type = self.payment_type_var.get()
            
            if not all([user_id, amount, payment_type]):
                messagebox.showerror("Error", "Please fill in all required fields")
                return
            
            try:
                amount = float(amount)
            except ValueError:
                messagebox.showerror("Error", "Amount must be a number")
                return
            
            response = requests.post(
                "http://localhost:5003/payments",
                params={"user_id": user_id, "amount": amount, "payment_type": payment_type}
            )
        
            if response.status_code == 200:
                messagebox.showinfo("Success", "Reservation and payment processed successfully")
                self.top.destroy()
                # Refresh parking spots and history after successful payment
                if hasattr(self.main_app, 'load_parking_spots'):
                    self.main_app.load_parking_spots()
                if hasattr(self.main_app, 'load_history'):
                    self.main_app.load_history()
            else:
                messagebox.showerror("Error", f"Failed to process payment: {response.text}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process payment: {str(e)}")
    
    def cancel_reservation(self):
        try:
            # Cancel the reservation by updating the spot back to available
            response = requests.post(
                f"http://localhost:5000/parking-spots/{self.spot_id_var.get()}/update",
                params={"status": "available", "user_id": None}
            )
            
            if response.status_code == 200:
                messagebox.showinfo("Cancelled", "Reservation cancelled successfully")
                self.top.destroy()
                # Refresh parking spots and history after cancellation
                if hasattr(self.main_app, 'load_parking_spots'):
                    self.main_app.load_parking_spots()
                if hasattr(self.main_app, 'load_history'):
                    self.main_app.load_history()
            else:
                messagebox.showerror("Error", f"Failed to cancel reservation: {response.text}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to cancel reservation: {str(e)}")

class ParkingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Parking Management System")
        self.root.geometry("800x600")
        
        # Create main notebook (tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        
        # Create tabs
        self.parking_tab = ttk.Frame(self.notebook)
        self.reservation_tab = ttk.Frame(self.notebook)
        self.history_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.parking_tab, text="Parking Spots")
        self.notebook.add(self.reservation_tab, text="Reservations")
        self.notebook.add(self.history_tab, text="History")
        
        # Initialize tabs
        self.setup_parking_tab()
        self.setup_reservation_tab()
        self.setup_history_tab()
        
        # Load initial data
        self.load_parking_spots()
        self.load_history()
    
    def setup_parking_tab(self):
        # Parking spots frame
        spots_frame = ttk.LabelFrame(self.parking_tab, text="Available Parking Spots")
        spots_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Treeview for parking spots
        self.spots_tree = ttk.Treeview(spots_frame, columns=("ID", "Status", "User ID"), show="headings")
        self.spots_tree.heading("ID", text="Spot ID")
        self.spots_tree.heading("Status", text="Status")
        self.spots_tree.heading("User ID", text="User ID")
        self.spots_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(spots_frame, orient="vertical", command=self.spots_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.spots_tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind selection event
        self.spots_tree.bind('<<TreeviewSelect>>', self.on_parking_spot_select)
        
        # Refresh button for parking spots
        ttk.Button(spots_frame, text="Refresh Parking Spots", command=self.load_parking_spots).pack(pady=5)
        
        # Update spot frame
        update_frame = ttk.LabelFrame(self.parking_tab, text="Update Spot Status")
        update_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(update_frame, text="Spot ID:").grid(row=0, column=0, padx=5, pady=5)
        self.spot_id_var = tk.StringVar()
        ttk.Entry(update_frame, textvariable=self.spot_id_var, state='readonly').grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(update_frame, text="Status:").grid(row=1, column=0, padx=5, pady=5)
        self.status_var = tk.StringVar()
        ttk.Combobox(update_frame, textvariable=self.status_var, values=["available", "reserved"]).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(update_frame, text="User ID:").grid(row=2, column=0, padx=5, pady=5)
        self.user_id_var = tk.StringVar()
        ttk.Entry(update_frame, textvariable=self.user_id_var).grid(row=2, column=1, padx=5, pady=5)
        
        # Add clear button and update button
        ttk.Button(update_frame, text="Clear Selection", command=self.clear_update_fields).grid(row=3, column=0, pady=10)
        ttk.Button(update_frame, text="Update Spot", command=self.update_spot).grid(row=3, column=1, pady=10)
    
    def setup_reservation_tab(self):
        # Reservation frame
        reservation_frame = ttk.LabelFrame(self.reservation_tab, text="Create Reservation")
        reservation_frame.pack(fill='x', padx=10, pady=10)
        
        # Available spots list
        spots_frame = ttk.LabelFrame(self.reservation_tab, text="Available Spots")
        spots_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.available_spots_tree = ttk.Treeview(spots_frame, columns=("ID", "Status"), show="headings")
        self.available_spots_tree.heading("ID", text="Spot ID")
        self.available_spots_tree.heading("Status", text="Status")
        
        # Set column widths
        self.available_spots_tree.column("ID", width=100)
        self.available_spots_tree.column("Status", width=100)
        
        self.available_spots_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(spots_frame, orient="vertical", command=self.available_spots_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.available_spots_tree.configure(yscrollcommand=scrollbar.set)
        
        # Bind selection event
        self.available_spots_tree.bind('<<TreeviewSelect>>', self.on_spot_select)
        
        ttk.Label(reservation_frame, text="User ID:").grid(row=0, column=0, padx=5, pady=5)
        self.reserve_user_id_var = tk.StringVar()
        ttk.Entry(reservation_frame, textvariable=self.reserve_user_id_var).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(reservation_frame, text="Spot ID:").grid(row=1, column=0, padx=5, pady=5)
        self.reserve_spot_id_var = tk.StringVar()
        ttk.Entry(reservation_frame, textvariable=self.reserve_spot_id_var, state='readonly').grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Button(reservation_frame, text="Create Reservation", command=self.create_reservation).grid(row=2, column=0, columnspan=2, pady=10)
        
        # Refresh button for available spots
        ttk.Button(spots_frame, text="Refresh Available Spots", command=self.load_available_spots).pack(pady=5)
        
        # Load available spots initially
        self.load_available_spots()
    
    def setup_history_tab(self):
        # History frame
        history_frame = ttk.LabelFrame(self.history_tab, text="Reservation History")
        history_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Treeview for history
        self.history_tree = ttk.Treeview(history_frame, columns=("Time", "Spot ID", "User ID"), show="headings")
        self.history_tree.heading("Time", text="Time")
        self.history_tree.heading("Spot ID", text="Spot ID")
        self.history_tree.heading("User ID", text="User ID")
        
        # Set column widths
        self.history_tree.column("Time", width=150)
        self.history_tree.column("Spot ID", width=100)
        self.history_tree.column("User ID", width=100)
        
        self.history_tree.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
        # Refresh button
        ttk.Button(history_frame, text="Refresh History", command=self.load_history).pack(pady=5)
    
    def load_history(self):
        try:
            # Clear existing items first
            for item in self.history_tree.get_children():
                self.history_tree.delete(item)

            response = requests.get("http://localhost:5004/history")
            if response.status_code == 200:
                history = response.json()
                for reservation in history:
                    try:
                        # Parse the timestamp and format it
                        timestamp_str = reservation.get("timestamp", "")
                        if timestamp_str:
                            # Parse the ISO format timestamp
                            timestamp = datetime.fromisoformat(timestamp_str.replace('T', ' ').split('.')[0])
                            # Format it in a more readable way
                            formatted_time = timestamp.strftime("%d/%m/%Y %H:%M:%S")
                        else:
                            formatted_time = ""
                        
                        spot_id = reservation.get("spot_id", "")
                        user_id = reservation.get("user_id", "")
                        self.history_tree.insert("", 0, values=(formatted_time, spot_id, user_id))
                    except Exception as e:
                        print(f"Error processing reservation entry: {str(e)}")
                        continue
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load history: {str(e)}")
            print(f"History loading error details: {str(e)}")  # For debugging
    
    def load_parking_spots(self):
        try:
            response = requests.get("http://localhost:5000/parking-spots")
            if response.status_code == 200:
                spots = response.json()
                # Clear existing items
                for item in self.spots_tree.get_children():
                    self.spots_tree.delete(item)
                # Add new items
                for spot in spots:
                    self.spots_tree.insert("", "end", values=(spot["id"], spot["status"], spot["user_id"]))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load parking spots: {str(e)}")
    
    def on_parking_spot_select(self, event):
        selected_items = self.spots_tree.selection()
        if selected_items:
            item = selected_items[0]
            values = self.spots_tree.item(item)['values']
            self.spot_id_var.set(values[0])  # Spot ID
            self.status_var.set(values[1])   # Status
            self.user_id_var.set(values[2] if values[2] != "None" else "")  # User ID
    
    def clear_update_fields(self):
        self.spot_id_var.set("")
        self.status_var.set("")
        self.user_id_var.set("")
        # Clear tree selection
        for item in self.spots_tree.selection():
            self.spots_tree.selection_remove(item)
    
    def update_spot(self):
        try:
            spot_id = self.spot_id_var.get()
            status = self.status_var.get()
            user_id = self.user_id_var.get() if self.user_id_var.get() else None
            
            if not all([spot_id, status]):
                messagebox.showerror("Error", "Please select a spot and specify the status")
                return
            
            # If status is available, clear the user ID
            if status == "available":
                user_id = None
            # If status is reserved, require a user ID
            elif status == "reserved" and not user_id:
                messagebox.showerror("Error", "Please provide a User ID for reserved spots")
                return
            
            # Check if user ID is already in use (only for reserved status)
            if status == "reserved" and user_id:
                try:
                    response = requests.get("http://localhost:5000/parking-spots")
                    if response.status_code == 200:
                        spots = response.json()
                        for spot in spots:
                            if spot["user_id"] == user_id and spot["id"] != spot_id:
                                messagebox.showerror("Error", "This User ID already has an active reservation")
                                return
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to check user ID: {str(e)}")
                    return
            
            response = requests.post(
                f"http://localhost:5000/parking-spots/{spot_id}/update",
                params={"status": status, "user_id": user_id}
            )
            
            if response.status_code == 200:
                messagebox.showinfo("Success", "Spot updated successfully")
                self.load_parking_spots()
                self.load_history()
                self.clear_update_fields()
            else:
                messagebox.showerror("Error", f"Failed to update spot: {response.text}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update spot: {str(e)}")
    
    def create_reservation(self):
        try:
            user_id = self.reserve_user_id_var.get()
            spot_id = self.reserve_spot_id_var.get()
            
            if not all([user_id, spot_id]):
                messagebox.showerror("Error", "Please fill in all required fields")
                return
            
            # Check if user ID is already in use
            try:
                response = requests.get("http://localhost:5000/parking-spots")
                if response.status_code == 200:
                    spots = response.json()
                    for spot in spots:
                        if spot["user_id"] == user_id:
                            messagebox.showerror("Error", "This User ID already has an active reservation")
                            return
            except Exception as e:
                messagebox.showerror("Error", f"Failed to check user ID: {str(e)}")
                return
            
            # Create temporary reservation
            response = requests.post(
                "http://localhost:5001/reservations",
                params={"user_id": user_id, "spot_id": spot_id}
            )
            
            if response.status_code == 200:
                # Show payment popup
                PaymentPopup(self.root, user_id, spot_id)  # Pass self.root instead of self
            else:
                messagebox.showerror("Error", f"Failed to create reservation: {response.text}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create reservation: {str(e)}")
    
    def load_available_spots(self):
        try:
            response = requests.get("http://localhost:5000/parking-spots")
            if response.status_code == 200:
                spots = response.json()
                # Clear existing items
                for item in self.available_spots_tree.get_children():
                    self.available_spots_tree.delete(item)
                # Add only available spots
                for spot in spots:
                    if spot["status"] == "available":
                        self.available_spots_tree.insert("", "end", values=(spot["id"], spot["status"]))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load available spots: {str(e)}")
    
    def on_spot_select(self, event):
        selected_items = self.available_spots_tree.selection()
        if selected_items:
            item = selected_items[0]
            spot_id = self.available_spots_tree.item(item)['values'][0]
            self.reserve_spot_id_var.set(spot_id)

if __name__ == "__main__":
    root = tk.Tk()
    app = ParkingGUI(root)
    root.mainloop() 