package com.pajamatalk.desktop

import androidx.compose.ui.window.Window
import androidx.compose.ui.window.application
import com.pajamatalk.shared.PajamaTalkApp

fun main() = application {
    Window(
        onCloseRequest = ::exitApplication,
        title = "PajamaTalk",
    ) {
        PajamaTalkApp()
    }
}
