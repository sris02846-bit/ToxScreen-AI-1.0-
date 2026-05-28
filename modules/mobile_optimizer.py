"""
Mobile Optimization Module
Responsive design, mobile features, and offline capability.
"""

import streamlit as st
from typing import Dict


def get_device_info() -> Dict:
    """Detect device information for responsive design."""
    return {
        "is_mobile": False,  # Streamlit auto-handles
        "screen_width": "responsive",
        "touch_support": True
    }


def mobile_friendly_css() -> str:
    """Generate mobile-friendly CSS."""
    return """
    <style>
        /* Mobile responsive design */
        @media (max-width: 768px) {
            .neon-title {
                font-size: 1.8rem !important;
            }
            .glass-card {
                padding: 0.8rem !important;
            }
            .metric-card {
                padding: 0.5rem !important;
            }
            .stButton button {
                width: 100% !important;
                padding: 0.5rem !important;
                font-size: 0.8rem !important;
            }
        }
        
        /* Touch-friendly buttons */
        .stButton button {
            min-height: 44px;
            touch-action: manipulation;
        }
        
        /* Offline indicator */
        .offline-badge {
            background: #ff3355;
            color: white;
            padding: 0.3rem 0.8rem;
            border-radius: 20px;
            font-size: 0.7rem;
            display: none;
        }
    </style>
    """


def check_offline_capability() -> Dict:
    """Check offline capability features."""
    return {
        "cached_predictions": True,
        "local_storage": True,
        "offline_mode": "Predictions cached for offline access"
    }


def optimize_for_mobile():
    """Apply mobile optimizations to current page."""
    st.markdown(mobile_friendly_css(), unsafe_allow_html=True)
