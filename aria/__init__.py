"""
ARIA Protocol - Autonomous Responsible Intelligence Architecture
A peer-to-peer efficient AI inference protocol.

Released under MIT License.
"""

__version__ = "0.5.2"
__author__ = "Anthony MURGO"

from aria.node import ARIANode
from aria.consent import ARIAConsent
from aria.ledger import ProvenanceLedger
from aria.network import ARIANetwork
from aria.inference import InferenceEngine
from aria.proof import ProofOfUsefulWork, ProofOfSobriety
from aria.api import ARIAOpenAIServer
from aria.dashboard import ARIADashboard
from aria.bitnet_native import BitNetNative
from aria.model_manager import ModelManager
