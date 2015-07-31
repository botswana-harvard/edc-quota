

class QoutaMonitor(object):
    """Calculates and updates andmonitors quota value.
    """

    def __init__(self, request):
        pass

    def client_quota(self):
        """Return client quota."""
        pass

    def master_quota(self):
        """Return master server quota."""
        pass

    def quota_limit(self):
        """Return the master quota limit."""
        pass

    def calculate_new_quotas(self):
        """Calculate quota to allocate to clients."""
        pass

    def allocate_quota(self):
        """Allocate client quota."""
        pass

    def by_pass_quota(self):
        """Bypass quota limit."""
        pass
