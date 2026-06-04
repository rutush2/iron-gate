import streamlit as st
import httpx
import pandas as pd
import time

st.set_page_config(page_title="Iron Gate Command Center", layout="wide")
st.title("🛡️ Iron Gate: Live Command Center")

st.sidebar.header("Admin Authentication")
admin_key = st.sidebar.text_input("Enter Admin API Key", type="password")

if admin_key:
    try:
        with httpx.Client() as client:
            response = client.get(
                "http://127.0.0.1:8000/admin/metrics",
                headers={"X-API-KEY": admin_key},
            )
            response.raise_for_status()
            data = response.json()

        col1, col2, col3 = st.columns(3)
        col1.metric("Active Users (Current Window)", data["active_keys"])
        col2.metric("Connected Servers", len(data["target_servers"]))
        col3.metric("System Status", f"{data['status']} ✅")

        st.subheader("Upstream Targets Node Operational Status")
        health_data = data.get("upstream_health", {})
        if health_data:
            h_cols = st.columns(len(health_data))
            for idx, (server_url, status) in enumerate(health_data.items()):
                with h_cols[idx]:
                    if "HEALTHY" in status:
                        st.success(f"🟢 {server_url}\nStatus: {status}")
                    else:
                        st.error(f"🔴 {server_url}\nStatus: {status}")
        else:
            st.info("Initializing node tracking metrics...")

        chart_col, telemetry_col = st.columns(2)

        with chart_col:
            st.subheader("User Traffic Allocation")
            if data["rate_limit_usage"]:
                df_traffic = pd.DataFrame(
                    data["rate_limit_usage"].items(),
                    columns=["User Profile", "Recent Requests"],
                )
                st.bar_chart(df_traffic.set_index("User Profile"))
            else:
                st.info("No user profiles active.")

        with telemetry_col:
            st.subheader("Live Latency Tracking (ms)")
            perf_logs = data.get("performance_logs", [])
            if perf_logs:
                df_perf = pd.DataFrame(perf_logs)

                if "latency" in df_perf.columns and not df_perf.empty:
                    df_latency = df_perf[["latency"]].dropna()
                    st.line_chart(df_latency)
                else:
                    st.info("No numerical latency coordinates found.")

                st.subheader("HTTP Status Distribution")
                if "status_code" in df_perf.columns:
                    status_counts = df_perf["status_code"].value_counts().to_dict()
                    st.write(status_counts)
            else:
                st.info("Waiting for routing performance telemetry...")

    except Exception as e:
        st.error(f"Could not connect to Iron Gate Engine. {e}")

    time.sleep(2)
    st.rerun()
else:
    st.warning("Please enter your Admin API Key in the sidebar to view live metrics.")