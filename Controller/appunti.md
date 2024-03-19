Model: Continue to keep agent behaviors along with environmental definitions, entities, and rules. Additionally, raise
custom Events whenever significant milestones or updates emerge during simulations. It maintains the integrity of the
Model layer without being influenced by the Controller concerns.

View: Same role as before—provide methods for printing or logging current simulation states.

Controller: Assume responsibility for listening to raised Events from the Model, react accordingly, and apply
modifications to the ongoing process. Instantiate and kick off the simulation while also handling overall monitoring.

vediamo degli esempi:

Sure! Let me give you an example of a file inside the Controller folder, considering the event-driven architecture. We
can call the file event_listeners.py. Its purpose is to listen for custom events triggered in the Model and perform
desired operations based on the received data.

Suppose you want to trigger some visualization-related activities when particular milestones occur in the simulation.
Here's what the content of event_listeners.py might look like:

# controllers/event_listeners.py

def on_milestone_reached(data):
print("Milestone Reached:", data["name"], "at time", data["time"])

def register_model_events():
# Assuming the existence of a Messenger object capable of connecting Listeners to Models
# Register listener function to receive MilestoneReachedEvent
Messenger.connect(on_milestone_reached, Simulator.MilestoneReachedEvent)

Now, suppose you have another file responsible for setting up the whole simulation. Let's call it simulation_manager.py,
which looks like this:

# controllers/simulation_manager.py

from controllers.event_listeners import register_model_events
from models.your_model import YourModel

def start_simulation():
sim = YourModel()
register_model_events()
sim.run()

if __name__ == "__main__":
start_simulation()

As shown in the example, the event_listeners.py contains helper functions acting as listeners for specific events
originating from the Model. Meanwhile, the simulation_manager.py initializes the entire simulation flow, including
registration of event listeners. When the Model raises a MilestoneReachedEvent, the previously registered
on_milestone_reached function gets executed, demonstrating the event-driven nature of the solution.