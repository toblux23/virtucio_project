import tkinter as tk
from tkinter import ttk, messagebox
import requests
from datetime import datetime

class PaymentPopup:
    def __init__(self, parent, full_name, spot_id):
        self.top = tk.Toplevel(parent)
        self.top.title("Process Payment")
        self.top.geometry("400x400")
        
        self.top.transient(parent)
        self.top.grab_set()
        
        self.full_name = full_name
        self.spot_id = spot_id
        self.parent = parent

        
        payment_frame = ttk.LabelFrame(self.top, text="Payment Details")
        payment_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(payment_frame, text="Full Name:").grid(row=0, column=0, padx=5, pady=5)
        self.full_name_var = tk.StringVar(value=full_name)
        ttk.Entry(payment_frame, textvariable=self.full_name_var, state='readonly').grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(payment_frame, text="Spot ID:").grid(row=1, column=0, padx=5, pady=5)
        self.spot_id_var = tk.StringVar(value=spot_id)
        ttk.Entry(payment_frame, textvariable=self.spot_id_var, state='readonly').grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(payment_frame, text="Start Time:").grid(row=2, column=0, padx=5, pady=5)
        self.start_time_var = tk.StringVar()
        ttk.Entry(payment_frame, textvariable=self.start_time_var).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Label(payment_frame, text="End Time:").grid(row=3, column=0, padx=5, pady=5)
        self.end_time_var = tk.StringVar()
        ttk.Entry(payment_frame, textvariable=self.end_time_var).grid(row=3, column=1, padx=5, pady=5)
        
        ttk.Label(payment_frame, text="Amount:").grid(row=4, column=0, padx=5, pady=5)
        self.amount_var = tk.StringVar(value="10.00")
        ttk.Entry(payment_frame, textvariable=self.amount_var, state='readonly').grid(row=4, column=1, padx=5, pady=5)
        ttk.Entry(payment_frame, textvariable=self.amount_var).grid(row=4, column=1, padx=5, pady=5)
        
        ttk.Label(payment_frame, text="Payment Type:").grid(row=5, column=0, padx=5, pady=5)
        self.payment_type_var = tk.StringVar(value="Maya")
        ttk.Combobox(payment_frame, textvariable=self.payment_type_var, 
                    values=["GCASH", "Maya", "Cash"]).grid(row=5, column=1, padx=5, pady=5)
        
        ttk.Button(payment_frame, text="Process Payment", command=self.process_payment).grid(row=6, column=0, columnspan=2, pady=10)
        ttk.Button(payment_frame, text="Cancel", command=self.cancel_reservation).grid(row=7, column=0, columnspan=2, pady=5)
    
    def process_payment(self):
        if not self.payment_type_var.get():
            messagebox.showerror("Error", "Please select a payment type")
            return
            
        if not self.start_time_var.get() or not self.end_time_var.get():
            messagebox.showerror("Error", "Please enter both start and end times")
            return
            
        try:
            response = requests.post(
                "http://localhost:5001/reservations",
                json={
                    "full_name": self.full_name, 
                    "spot_id": self.spot_id,
                    "payment_type": self.payment_type_var.get(),
                    "start_time": self.start_time_var.get(),
                    "end_time": self.end_time_var.get()
                }
            )
            
            if response.status_code == 200:
                # Show success message
                messagebox.showinfo("Success", "Payment and reservation processed successfully")
                
                # Show notification popup
                notification = tk.Toplevel(self.parent)
                notification.title("Reservation Notification")
                notification.geometry("300x200")
                
                # Center the notification
                notification.transient(self.parent)
                notification.grab_set()
                
                # Add notification content
                ttk.Label(notification, text="Reservation Successful!", font=("Arial", 12, "bold")).pack(pady=10)
                ttk.Label(notification, text=f"Spot ID: {self.spot_id}").pack()
                ttk.Label(notification, text=f"Start Time: {self.start_time_var.get()}").pack()
                ttk.Label(notification, text=f"End Time: {self.end_time_var.get()}").pack()
                ttk.Label(notification, text=f"Payment Type: {self.payment_type_var.get()}").pack()
                ttk.Label(notification, text=f"Amount: ₱10.00").pack()
                
                # Add close button
                ttk.Button(notification, text="Close", command=notification.destroy).pack(pady=10)
                
                # Close payment window
                self.top.destroy()
            else:
                error_detail = response.json().get("detail", "Unknown error")
                messagebox.showerror("Error", f"Failed to process payment and create reservation: {error_detail}")
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"Could not connect to services: {str(e)}")
    
    def cancel_reservation(self):
        self.top.destroy()

class ParkingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Parking Management System")
        self.root.geometry("800x600")


        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)
        

        self.reservation_tab = ttk.Frame(self.notebook)
        self.admin_tab = ttk.Frame(self.notebook)
        self.history_tab = ttk.Frame(self.notebook)
        

        self.notebook.add(self.reservation_tab, text="Reservations")
        self.notebook.add(self.admin_tab, text="Active Parkings")
        self.notebook.add(self.history_tab, text="History")
        

        self.setup_reservation_tab()
        self.setup_admin_tab()
        self.setup_history_tab()
        

        self.load_available_spots()
        self.load_history()
    
    def setup_admin_tab(self):

        spots_frame = ttk.LabelFrame(self.admin_tab, text="Parking Spots Management")
        spots_frame.pack(fill='both', expand=True, padx=10, pady=10)


        self.spots_tree = ttk.Treeview(spots_frame, columns=("ID", "Status", "Full Name"), show="headings")
        self.spots_tree.heading("ID", text="Spot ID")
        self.spots_tree.heading("Status", text="Status")
        self.spots_tree.heading("Full Name", text="Full Name")
        

        self.spots_tree.column("ID", width=100)
        self.spots_tree.column("Status", width=100)
        self.spots_tree.column("Full Name", width=150)
        
        self.spots_tree.pack(fill='both', expand=True, padx=5, pady=5)
        

        scrollbar = ttk.Scrollbar(spots_frame, orient="vertical", command=self.spots_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.spots_tree.configure(yscrollcommand=scrollbar.set)
        

        self.spots_tree.bind('<<TreeviewSelect>>', self.on_parking_spot_select)
        

        ttk.Button(spots_frame, text="Refresh Parking Spots", command=self.load_parking_spots).pack(pady=5)
        

        update_frame = ttk.LabelFrame(self.admin_tab, text="Update Spot Status")
        update_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(update_frame, text="Spot ID:").grid(row=0, column=0, padx=5, pady=5)
        self.spot_id_var = tk.StringVar()
        ttk.Entry(update_frame, textvariable=self.spot_id_var, state='readonly').grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(update_frame, text="Status:").grid(row=1, column=0, padx=5, pady=5)
        self.status_var = tk.StringVar()
        ttk.Combobox(update_frame, textvariable=self.status_var, 
                    values=["available", "reserved"]).grid(row=1, column=1, padx=5, pady=5)
        
        ttk.Label(update_frame, text="Full Name:").grid(row=2, column=0, padx=5, pady=5)
        self.full_name_var = tk.StringVar()
        ttk.Entry(update_frame, textvariable=self.full_name_var).grid(row=2, column=1, padx=5, pady=5)
        
        ttk.Button(update_frame, text="Clear Selection", command=self.clear_update_fields).grid(row=3, column=0, pady=10)
        ttk.Button(update_frame, text="Update Spot", command=self.update_spot).grid(row=3, column=1, pady=10)
        

        self.load_parking_spots()
    
    def on_parking_spot_select(self, event):
        selected_items = self.spots_tree.selection()
        if selected_items:
            item = selected_items[0]
            values = self.spots_tree.item(item)['values']
            self.spot_id_var.set(values[0])
            self.status_var.set(values[1])
            self.full_name_var.set(values[2] if values[2] != "None" else "")
    
    def clear_update_fields(self):
        self.spot_id_var.set("")
        self.status_var.set("")
        self.full_name_var.set("")
    
    def update_spot(self):
        spot_id = self.spot_id_var.get()
        status = self.status_var.get()
        full_name = self.full_name_var.get()
        
        if not spot_id:
            messagebox.showerror("Error", "Please select a spot to update")
            return
            
        if not status:
            messagebox.showerror("Error", "Please select a status")
            return
            

        if status == "available":
            full_name = None
            
        try:
            response = requests.post(
                f"http://localhost:5000/parking-spots/{spot_id}/update",
                params={
                    "status": status,
                    "full_name": full_name
                }
            )
            
            if response.status_code == 200:
                messagebox.showinfo("Success", "Spot updated successfully")
                self.load_parking_spots() 
                self.clear_update_fields() 
            else:
                error_detail = response.json().get("detail", "Unknown error")
                messagebox.showerror("Error", f"Failed to update spot: {error_detail}")
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "Could not connect to parking service")
    
    def load_parking_spots(self):
        try:

            for item in self.spots_tree.get_children():
                self.spots_tree.delete(item)
            

            response = requests.get("http://localhost:5000/parking-spots")
            if response.status_code == 200:
                spots = response.json()
                for spot in spots:
                    self.spots_tree.insert("", "end", values=(
                        spot["id"],
                        spot["status"],
                        spot.get("full_name", "") 
                    ))
            else:
                messagebox.showerror("Error", "Failed to load parking spots")
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "Could not connect to parking service")
    
    def setup_reservation_tab(self):
        main_frame = ttk.Frame(self.reservation_tab)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        left_frame = ttk.LabelFrame(main_frame, text="Create Reservation")
        left_frame.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        

        form_frame = ttk.Frame(left_frame)
        form_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        ttk.Label(form_frame, text="Full Name:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.reserve_full_name_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.reserve_full_name_var, width=30).grid(row=0, column=1, padx=5, pady=5)
        
        ttk.Label(form_frame, text="Spot ID:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.reserve_spot_id_var = tk.StringVar()
        ttk.Entry(form_frame, textvariable=self.reserve_spot_id_var, state='readonly', width=30).grid(row=1, column=1, padx=5, pady=5)
        

        ttk.Button(form_frame, text="Create Reservation", command=self.create_reservation).grid(row=2, column=0, columnspan=2, pady=20)
        

        right_frame = ttk.LabelFrame(main_frame, text="Available Spots")
        right_frame.pack(side='right', fill='y', padx=5, pady=5)
        
        self.available_spots_tree = ttk.Treeview(right_frame, columns=("ID", "Status"), show="headings", height=10)
        self.available_spots_tree.heading("ID", text="Spot ID")
        self.available_spots_tree.heading("Status", text="Status")
        

        self.available_spots_tree.column("ID", width=100)
        self.available_spots_tree.column("Status", width=100)
        
        self.available_spots_tree.pack(fill='y', padx=5, pady=5)
        

        scrollbar = ttk.Scrollbar(right_frame, orient="vertical", command=self.available_spots_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.available_spots_tree.configure(yscrollcommand=scrollbar.set)
        

        self.available_spots_tree.bind('<<TreeviewSelect>>', self.on_spot_select)
        

        ttk.Button(right_frame, text="Refresh Available Spots", command=self.load_available_spots).pack(pady=5)
    
    def setup_history_tab(self):

        history_frame = ttk.LabelFrame(self.history_tab, text="Reservation History")
        history_frame.pack(fill='both', expand=True, padx=10, pady=10)
        

        self.history_tree = ttk.Treeview(history_frame, columns=("Time", "Spot ID", "Full Name", "Payment Type", "Start Time", "End Time"), show="headings")
        self.history_tree.heading("Time", text="Time")
        self.history_tree.heading("Spot ID", text="Spot ID")
        self.history_tree.heading("Full Name", text="Full Name")
        self.history_tree.heading("Payment Type", text="Payment Type")
        self.history_tree.heading("Start Time", text="Start Time")
        self.history_tree.heading("End Time", text="End Time")


        self.history_tree.column("Time", width=150)
        self.history_tree.column("Spot ID", width=100)
        self.history_tree.column("Full Name", width=100)
        self.history_tree.column("Payment Type", width=100)
        self.history_tree.column("Start Time", width=100)
        self.history_tree.column("End Time", width=100)
        
        self.history_tree.pack(fill='both', expand=True, padx=5, pady=5)
        

        scrollbar = ttk.Scrollbar(history_frame, orient="vertical", command=self.history_tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.history_tree.configure(yscrollcommand=scrollbar.set)
        
 
        ttk.Button(history_frame, text="Refresh History", command=self.load_history).pack(pady=5)
        

        self.load_history()
    
    def load_history(self):
        try:

            for item in self.history_tree.get_children():
                self.history_tree.delete(item)
            

            response = requests.get("http://localhost:5004/history")
            if response.status_code == 200:
                history = response.json()
                for record in history:

                    timestamp = datetime.fromisoformat(record["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")
                    self.history_tree.insert("", "end", values=(
                        timestamp,
                        record["spot_id"],
                        record["full_name"],
                        record.get("payment_type", "N/A"),
                        record.get("start_time", "N/A"),
                        record.get("end_time", "N/A")
                    ))
            else:
                messagebox.showerror("Error", "Failed to load history")
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "Could not connect to history service")
    
    def load_available_spots(self):
        try:
            
            for item in self.available_spots_tree.get_children():
                self.available_spots_tree.delete(item)
            
            response = requests.get("http://localhost:5000/parking-spots")
            if response.status_code == 200:
                spots = response.json()
                for spot in spots:
                    if spot["status"] == "available":
                        self.available_spots_tree.insert("", "end", values=(spot["id"], spot["status"]))
            else:
                messagebox.showerror("Error", "Failed to load available spots")
        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "Could not connect to parking service")
    
    def on_spot_select(self, event):
        selected_items = self.available_spots_tree.selection()
        if selected_items:
            item = selected_items[0]
            spot_id = self.available_spots_tree.item(item)['values'][0]
            self.reserve_spot_id_var.set(spot_id)
    
    def create_reservation(self):
        full_name = self.reserve_full_name_var.get()
        spot_id = self.reserve_spot_id_var.get()
        
        if not full_name or not spot_id:
            messagebox.showerror("Error", "Please select a spot and enter your full name.")
            return
        

        PaymentPopup(self.root, full_name, spot_id)

if __name__ == "__main__":
    root = tk.Tk()
    app = ParkingGUI(root)
    root.mainloop() 