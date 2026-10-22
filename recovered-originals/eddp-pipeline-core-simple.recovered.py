# -------------------------
# TEMPLATE RENDERING
# -------------------------
def render(self, template: Dict, data: Dict) -> Dict:
    return {
        "title": template.get("title"),
        "sections": template.get("sections"),
        "kpis": data.get("kpis"),
        "timestamp": data.get("timestamp")
    }

# -------------------------
# ROLE ROUTING
# -------------------------
def route(self, role_map: Dict[str, List[str]], role: str) -> List[str]:
    return role_map.get(role, [])

# -------------------------
# DELIVERY
# -------------------------
def deliver(self, recipients: List[str], dashboard: Dict, channel: str):
    event = {
        "timestamp": time.time(),
        "recipients": recipients,
        "channel": channel,
        "dashboard": dashboard,
        "status": "DELIVERED"
    }
    self.delivery_log.append(event)
    return event

# -------------------------
# MAIN PIPELINE
# -------------------------
def execute(self, payload: Dict, template: Dict, role_map: Dict, role: str, channel="email"):
    dashboard = self.render(template, payload)
    recipients = self.route(role_map, role)
    return self.deliver(recipients, dashboard, channel)