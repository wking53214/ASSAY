"""A test module that is green and proves nothing.

CONSTRUCTED SPECIMEN, and says so. The other named specimens in this corpus
are recovered files. This one reproduces a failure recorded in the
ecosystem's own history (sentinel_os, finding F9: tests whose assertions sat
behind guards that were never true, so every test returned without asserting
and the suite stayed green while the code was broken) in the smallest shape
that still has every property of the original:

  * `test_governance_boots` has no body. It cannot fail. It is counted.
  * `test_audit_ring_pushes` does work and asserts nothing: it passes
    whenever the code does not raise, whatever the code did.
  * `test_quorum_is_reached` asserts, but only behind a guard that the
    module's own constant makes false forever. The assertion never runs.
  * `test_gateway_is_called` asserts only on a mock: it proves the code
    called the mock, which is a fact about the test's own wiring.

Run it: four tests, four passes, and nothing about the governance kernel is
known afterwards. A count of passing tests that includes these is one too
high four times over.
"""

from unittest.mock import Mock

STRICT_MODE = False


class GovernanceKernel:
    def __init__(self):
        self.ring = []
        self.quorum = 0

    def boot(self):
        return True

    def push(self, event):
        # The audit ring that was never read back: the push "works" and the
        # ring is never consulted by anything.
        self.ring.append(event)

    def reach_quorum(self, votes):
        self.quorum = len(votes)
        return self.quorum >= 3


def test_governance_boots():
    pass


def test_audit_ring_pushes():
    kernel = GovernanceKernel()
    kernel.boot()
    kernel.push({"actor": "operator", "action": "seal"})


def test_quorum_is_reached():
    kernel = GovernanceKernel()
    reached = kernel.reach_quorum(["a", "b"])
    if STRICT_MODE:
        assert reached


def test_gateway_is_called():
    gateway = Mock()
    kernel = GovernanceKernel()
    kernel.boot()
    gateway.submit(kernel.quorum)
    gateway.submit.assert_called_once()
