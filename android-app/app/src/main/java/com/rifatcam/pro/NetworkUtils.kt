package com.rifatcam.pro

import android.content.Context
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.net.wifi.WifiManager
import java.net.Inet4Address
import java.net.InetAddress
import java.net.NetworkInterface
import java.net.SocketException

object NetworkUtils {

    const val STREAM_PORT = 8080
    const val DISCOVERY_PORT = 5005
    const val DISCOVERY_MAGIC = "RIFATCAM_DISCOVER"
    const val DISCOVERY_RESPONSE = "RIFATCAM_HERE"

    fun getLocalIpAddress(context: Context): String {
        try {
            val wifiManager = context.applicationContext
                .getSystemService(Context.WIFI_SERVICE) as? WifiManager
            if (wifiManager != null) {
                val wifiInfo = wifiManager.connectionInfo
                val ipInt = wifiInfo.ipAddress
                if (ipInt != 0) {
                    return String.format(
                        "%d.%d.%d.%d",
                        ipInt and 0xff,
                        ipInt shr 8 and 0xff,
                        ipInt shr 16 and 0xff,
                        ipInt shr 24 and 0xff
                    )
                }
            }
        } catch (e: Exception) {
            // Fall through to interface enumeration
        }

        try {
            val interfaces = NetworkInterface.getNetworkInterfaces()
            while (interfaces.hasMoreElements()) {
                val networkInterface = interfaces.nextElement()
                if (networkInterface.isUp && !networkInterface.isLoopback) {
                    val addresses = networkInterface.inetAddresses
                    while (addresses.hasMoreElements()) {
                        val addr = addresses.nextElement()
                        if (addr is Inet4Address && !addr.isLoopbackAddress) {
                            return addr.hostAddress ?: "127.0.0.1"
                        }
                    }
                }
            }
        } catch (e: SocketException) {
            e.printStackTrace()
        }

        return "127.0.0.1"
    }

    fun isWifiConnected(context: Context): Boolean {
        val connectivityManager =
            context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
        val network = connectivityManager.activeNetwork ?: return false
        val capabilities = connectivityManager.getNetworkCapabilities(network) ?: return false
        return capabilities.hasTransport(NetworkCapabilities.TRANSPORT_WIFI)
    }

    fun getStreamUrl(context: Context): String {
        val ip = getLocalIpAddress(context)
        return "http://$ip:$STREAM_PORT"
    }

    fun getVideoUrl(context: Context): String {
        return "${getStreamUrl(context)}/video"
    }
}
