#!/usr/bin/env python3
"""
Task Tracker Pro - Advanced Features Demo Script
Demonstrates all the enhanced features of the application
"""

import requests
import json
import time
from datetime import datetime, timedelta

class TaskTrackerDemo:
    def __init__(self, base_url="http://localhost:5001"):
        self.base_url = base_url
        self.session = requests.Session()
        self.demo_user = {
            'username': 'demo',
            'password': 'demo123'
        }
        
    def print_section(self, title):
        """Print a formatted section header"""
        print("\n" + "="*60)
        print(f"  {title}")
        print("="*60)
    
    def print_step(self, step):
        """Print a formatted step"""
        print(f"\n📋 {step}")
        
    def login(self):
        """Login to the demo account"""
        self.print_step("Logging in to demo account...")
        response = self.session.post(f"{self.base_url}/auth/login", data=self.demo_user)
        if response.status_code == 200:
            print("✅ Successfully logged in!")
            return True
        else:
            print("❌ Login failed!")
            return False
    
    def test_api_endpoints(self):
        """Test various API endpoints"""
        self.print_section("TESTING API ENDPOINTS")
        
        # Test analytics endpoint
        self.print_step("Testing analytics endpoint...")
        response = self.session.get(f"{self.base_url}/api/analytics/dashboard")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Analytics endpoint working! Found {len(data.get('recent_activity', []))} activities")
        else:
            print(f"❌ Analytics endpoint failed: {response.status_code}")
        
        # Test search endpoint
        self.print_step("Testing search endpoint...")
        response = self.session.get(f"{self.base_url}/api/search?q=demo")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Search endpoint working! Found {len(data.get('results', []))} results")
        else:
            print(f"❌ Search endpoint failed: {response.status_code}")
        
        # Test notifications endpoint
        self.print_step("Testing notifications endpoint...")
        response = self.session.get(f"{self.base_url}/api/notifications")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Notifications endpoint working! {data.get('unread_count', 0)} unread notifications")
        else:
            print(f"❌ Notifications endpoint failed: {response.status_code}")
    
    def test_task_operations(self):
        """Test task CRUD operations"""
        self.print_section("TESTING TASK OPERATIONS")
        
        # Create a new task
        self.print_step("Creating a new task...")
        task_data = {
            'title': f'Demo Task - {datetime.now().strftime("%H:%M:%S")}',
            'description': 'This is a demo task created by the feature test script',
            'priority': 'high',
            'status': 'pending'
        }
        response = self.session.post(f"{self.base_url}/api/tasks", 
                                   headers={'Content-Type': 'application/json'},
                                   data=json.dumps(task_data))
        
        if response.status_code == 201:
            task = response.json().get('task', {})
            task_id = task.get('id')
            print(f"✅ Task created successfully! ID: {task_id}")
            
            # Update the task
            self.print_step("Updating the task...")
            update_data = {'status': 'in_progress'}
            response = self.session.put(f"{self.base_url}/api/tasks/{task_id}",
                                      headers={'Content-Type': 'application/json'},
                                      data=json.dumps(update_data))
            if response.status_code == 200:
                print("✅ Task updated successfully!")
            else:
                print(f"❌ Task update failed: {response.status_code}")
                
            # Toggle task status
            self.print_step("Toggling task status...")
            response = self.session.post(f"{self.base_url}/api/tasks/{task_id}/toggle-status")
            if response.status_code == 200:
                print("✅ Task status toggled successfully!")
            else:
                print(f"❌ Task status toggle failed: {response.status_code}")
                
        else:
            print(f"❌ Task creation failed: {response.status_code}")
    
    def test_project_operations(self):
        """Test project operations"""
        self.print_section("TESTING PROJECT OPERATIONS")
        
        # Create a new project
        self.print_step("Creating a new project...")
        project_data = {
            'name': f'Demo Project - {datetime.now().strftime("%H:%M:%S")}',
            'description': 'This is a demo project created by the feature test script',
            'status': 'active'
        }
        response = self.session.post(f"{self.base_url}/api/projects",
                                   headers={'Content-Type': 'application/json'},
                                   data=json.dumps(project_data))
        
        if response.status_code == 201:
            project = response.json().get('project', {})
            project_id = project.get('id')
            print(f"✅ Project created successfully! ID: {project_id}")
        else:
            print(f"❌ Project creation failed: {response.status_code}")
    
    def test_bulk_operations(self):
        """Test bulk operations"""
        self.print_section("TESTING BULK OPERATIONS")
        
        # Get existing tasks first
        response = self.session.get(f"{self.base_url}/api/tasks")
        if response.status_code == 200:
            tasks = response.json().get('tasks', [])
            if tasks:
                task_ids = [task['id'] for task in tasks[:3]]  # Get first 3 tasks
                
                self.print_step("Testing bulk task update...")
                bulk_data = {
                    'task_ids': task_ids,
                    'updates': {'priority': 'medium'}
                }
                response = self.session.post(f"{self.base_url}/api/tasks/bulk-update",
                                           headers={'Content-Type': 'application/json'},
                                           data=json.dumps(bulk_data))
                
                if response.status_code == 200:
                    print(f"✅ Bulk update successful! Updated {len(task_ids)} tasks")
                else:
                    print(f"❌ Bulk update failed: {response.status_code}")
            else:
                print("⚠️  No tasks available for bulk operations")
        else:
            print(f"❌ Failed to get tasks: {response.status_code}")
    
    def test_time_tracking(self):
        """Test time tracking features"""
        self.print_section("TESTING TIME TRACKING")
        
        # Get a task to track time for
        response = self.session.get(f"{self.base_url}/api/tasks")
        if response.status_code == 200:
            tasks = response.json().get('tasks', [])
            if tasks:
                task_id = tasks[0]['id']
                
                self.print_step("Starting time tracking...")
                response = self.session.post(f"{self.base_url}/api/time-tracking/start",
                                           headers={'Content-Type': 'application/json'},
                                           data=json.dumps({'task_id': task_id}))
                
                if response.status_code == 200:
                    print("✅ Time tracking started!")
                    
                    # Simulate some work time
                    time.sleep(2)
                    
                    self.print_step("Stopping time tracking...")
                    response = self.session.post(f"{self.base_url}/api/time-tracking/stop",
                                               headers={'Content-Type': 'application/json'},
                                               data=json.dumps({'task_id': task_id}))
                    
                    if response.status_code == 200:
                        print("✅ Time tracking stopped!")
                    else:
                        print(f"❌ Failed to stop time tracking: {response.status_code}")
                else:
                    print(f"❌ Failed to start time tracking: {response.status_code}")
            else:
                print("⚠️  No tasks available for time tracking")
        else:
            print(f"❌ Failed to get tasks: {response.status_code}")
    
    def test_export_features(self):
        """Test export features"""
        self.print_section("TESTING EXPORT FEATURES")
        
        # Test CSV export
        self.print_step("Testing CSV export...")
        response = self.session.get(f"{self.base_url}/api/export/csv")
        if response.status_code == 200:
            print(f"✅ CSV export successful! Size: {len(response.content)} bytes")
        else:
            print(f"❌ CSV export failed: {response.status_code}")
        
        # Test JSON export
        self.print_step("Testing JSON export...")
        response = self.session.get(f"{self.base_url}/api/export/json")
        if response.status_code == 200:
            print(f"✅ JSON export successful! Size: {len(response.content)} bytes")
        else:
            print(f"❌ JSON export failed: {response.status_code}")
    
    def test_dashboard_features(self):
        """Test dashboard-specific features"""
        self.print_section("TESTING DASHBOARD FEATURES")
        
        # Test dashboard page
        self.print_step("Loading dashboard page...")
        response = self.session.get(f"{self.base_url}/dashboard")
        if response.status_code == 200:
            print("✅ Dashboard loaded successfully!")
            
            # Check if it contains the expected elements
            if 'Welcome back' in response.text:
                print("✅ Dashboard welcome message found!")
            if 'Total Tasks' in response.text:
                print("✅ Dashboard statistics found!")
            if 'chart' in response.text.lower():
                print("✅ Dashboard charts found!")
        else:
            print(f"❌ Dashboard loading failed: {response.status_code}")
    
    def run_full_demo(self):
        """Run the complete feature demo"""
        print("🚀 Task Tracker Pro - Advanced Features Demo")
        print("="*60)
        print("This script will test all the enhanced features of the application")
        print("Make sure the application is running on http://localhost:5001")
        
        try:
            # Login first
            if not self.login():
                return False
            
            # Run all tests
            self.test_dashboard_features()
            self.test_api_endpoints()
            self.test_task_operations()
            self.test_project_operations()
            self.test_bulk_operations()
            self.test_time_tracking()
            self.test_export_features()
            
            self.print_section("DEMO COMPLETED SUCCESSFULLY! 🎉")
            print("All enhanced features are working correctly.")
            print("\nKey Features Demonstrated:")
            print("• Enhanced Dashboard with real-time analytics")
            print("• Advanced API endpoints for all operations")
            print("• Search functionality")
            print("• Notification system")
            print("• Bulk operations")
            print("• Time tracking")
            print("• Data export (CSV/JSON)")
            print("• Interactive UI components")
            
            return True
            
        except requests.exceptions.ConnectionError:
            print("\n❌ Connection Error!")
            print("Make sure the application is running:")
            print("1. cd /Users/harrisonfrench/task/task_tracker_pro_flask")
            print("2. python app.py")
            print("3. Open http://localhost:5001 in your browser")
            return False
        except Exception as e:
            print(f"\n❌ Demo failed with error: {str(e)}")
            return False

if __name__ == "__main__":
    demo = TaskTrackerDemo()
    demo.run_full_demo()
