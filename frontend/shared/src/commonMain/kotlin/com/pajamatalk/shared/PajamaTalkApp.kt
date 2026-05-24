package com.pajamatalk.shared

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.ExperimentalFoundationApi
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.gestures.detectDragGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.rounded.AutoAwesome
import androidx.compose.material.icons.rounded.Bookmarks
import androidx.compose.material.icons.rounded.Coffee
import androidx.compose.material.icons.rounded.FlightTakeoff
import androidx.compose.material.icons.rounded.Home
import androidx.compose.material.icons.rounded.Mic
import androidx.compose.material.icons.rounded.Person
import androidx.compose.material.icons.rounded.Psychology
import androidx.compose.material.icons.rounded.Work
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Tab
import androidx.compose.material3.TabRow
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.runtime.staticCompositionLocalOf
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.draw.scale
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.rotate
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import cafe.adriel.voyager.navigator.tab.CurrentTab
import cafe.adriel.voyager.navigator.tab.LocalTabNavigator
import cafe.adriel.voyager.navigator.tab.Tab
import cafe.adriel.voyager.navigator.tab.TabNavigator
import cafe.adriel.voyager.navigator.tab.TabOptions
import com.pajamatalk.shared.data.ContextAnalyzeDto
import com.pajamatalk.shared.data.PajamaAppState
import com.pajamatalk.shared.data.ReviewGrade
import com.pajamatalk.shared.data.SpeakingRoomDto
import com.pajamatalk.shared.data.WordDto
import kotlinx.coroutines.launch
import kotlin.math.roundToInt

private val Lavender = Color(0xFFE8DEF8)
private val SoftLilac = Color(0xFFF7F1FF)
private val Peach = Color(0xFFF3B6A8)
private val Mint = Color(0xFF9DCEC0)
private val Butter = Color(0xFFFFD982)
private val Graphite = Color(0xFF28242F)
private val InkMuted = Color(0xFF6E6578)
private val LocalPajamaState = staticCompositionLocalOf<PajamaAppState> {
    error("PajamaAppState was not provided.")
}

@Composable
fun PajamaTalkApp() {
    val appState = remember { PajamaAppState() }
    LaunchedEffect(Unit) {
        appState.boot()
    }

    MaterialTheme(
        colorScheme = lightColorScheme(
            primary = Graphite,
            secondary = Peach,
            tertiary = Mint,
            surface = SoftLilac,
            background = Color(0xFFFFFBFF),
            onPrimary = Color.White,
            onSurface = Graphite,
        ),
    ) {
        Surface(
            modifier = Modifier.fillMaxSize(),
            color = MaterialTheme.colorScheme.background,
        ) {
            CompositionLocalProvider(LocalPajamaState provides appState) {
                TabNavigator(AuraTab) {
                    Scaffold(
                        contentWindowInsets = WindowInsets(0.dp),
                        bottomBar = { PajamaBottomBar() },
                    ) { padding ->
                        Box(
                            modifier = Modifier
                                .fillMaxSize()
                                .padding(padding)
                                .background(
                                    Brush.verticalGradient(
                                        listOf(Color(0xFFFFFBFF), Color(0xFFF8F1FF), Color(0xFFFFF4EE)),
                                    ),
                                )
                                .imePadding(),
                        ) {
                            CurrentTab()
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun PajamaBottomBar() {
    NavigationBar(
        modifier = Modifier.navigationBarsPadding(),
        containerColor = Color.White.copy(alpha = 0.92f),
        tonalElevation = 0.dp,
    ) {
        PajamaTabItem(AuraTab, Icons.Rounded.Home)
        PajamaTabItem(SpeakingTab, Icons.Rounded.Mic)
        PajamaTabItem(StorageTab, Icons.Rounded.Bookmarks)
        PajamaTabItem(VibeTab, Icons.Rounded.Person)
    }
}

@Composable
private fun RowScope.PajamaTabItem(tab: Tab, icon: ImageVector) {
    val tabNavigator = LocalTabNavigator.current
    val selected = tabNavigator.current.key == tab.key
    NavigationBarItem(
        selected = selected,
        onClick = { tabNavigator.current = tab },
        icon = { Icon(icon, contentDescription = tab.options.title) },
        label = { Text(tab.options.title, maxLines = 1, overflow = TextOverflow.Ellipsis) },
    )
}

private object AuraTab : Tab {
    override val options: TabOptions
        @Composable get() = remember { TabOptions(index = 0u, title = "Aura") }

    @Composable
    override fun Content() = AuraScreen()
}

private object SpeakingTab : Tab {
    override val options: TabOptions
        @Composable get() = remember { TabOptions(index = 1u, title = "Speak") }

    @Composable
    override fun Content() = SpeakingRoomsScreen()
}

private object StorageTab : Tab {
    override val options: TabOptions
        @Composable get() = remember { TabOptions(index = 2u, title = "Storage") }

    @Composable
    override fun Content() = StorageScreen()
}

private object VibeTab : Tab {
    override val options: TabOptions
        @Composable get() = remember { TabOptions(index = 3u, title = "Vibe") }

    @Composable
    override fun Content() = VibeScreen()
}

@Composable
private fun ScreenFrame(content: @Composable ColumnScope.() -> Unit) {
    BoxWithConstraints(
        modifier = Modifier
            .fillMaxSize()
            .statusBarsPadding(),
    ) {
        val horizontal = if (maxWidth < 420.dp) 18.dp else 32.dp
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = horizontal),
            verticalArrangement = Arrangement.spacedBy(18.dp),
            contentPadding = androidx.compose.foundation.layout.PaddingValues(top = 18.dp, bottom = 22.dp),
        ) {
            item {
                Column(
                    verticalArrangement = Arrangement.spacedBy(18.dp),
                    content = content,
                )
            }
        }
    }
}

@Composable
private fun AuraScreen() {
    val appState = LocalPajamaState.current
    val scope = rememberCoroutineScope()
    var contextText by remember { mutableStateOf("") }

    ScreenFrame {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Column {
                Text("PajamaTalk", fontSize = 28.sp, fontWeight = FontWeight.Black, color = Graphite)
                Text("5 min chill streak", color = InkMuted, fontWeight = FontWeight.Medium)
            }
            CandleBadge(days = 7)
        }

        ConnectionStatus(appState)
        AuraHero()

        CozyCard(background = Color.White.copy(alpha = 0.84f)) {
            Text("Alex is waiting in the cafe", fontSize = 21.sp, fontWeight = FontWeight.Bold, color = Graphite)
            Spacer(Modifier.height(8.dp))
            Text("A tiny speaking quest, oat milk energy included.", color = InkMuted)
            Spacer(Modifier.height(14.dp))
            SoftAction("Enter room", Icons.Rounded.Coffee, Peach, onClick = {})
        }

        CozyCard(background = Lavender.copy(alpha = 0.72f)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Rounded.AutoAwesome, contentDescription = null, tint = Graphite)
                Spacer(Modifier.width(10.dp))
                Text("Context Buddy", fontSize = 20.sp, fontWeight = FontWeight.Bold, color = Graphite)
            }
            Spacer(Modifier.height(12.dp))
            OutlinedTextField(
                value = contextText,
                onValueChange = { contextText = it },
                modifier = Modifier
                    .fillMaxWidth()
                    .height(122.dp),
                shape = RoundedCornerShape(28.dp),
                placeholder = { Text("Paste a line that caught you") },
            )
            Spacer(Modifier.height(12.dp))
            SoftAction(
                text = if (appState.isAnalyzingContext) "Analyzing" else "Analyze",
                icon = Icons.Rounded.Psychology,
                color = Mint,
                enabled = !appState.isAnalyzingContext && contextText.trim().length >= 3,
                onClick = {
                    scope.launch { appState.analyzeContext(contextText) }
                },
            )
            appState.contextResult?.let { result ->
                Spacer(Modifier.height(14.dp))
                ContextResultCard(
                    result = result,
                    isAdding = appState.isAddingWord,
                    onAddAll = { scope.launch { appState.addContextSuggestions() } },
                    onClear = { appState.clearContextResult() },
                )
            }
        }

        GrammarNudge()
    }
}

@Composable
private fun AuraHero() {
    CozyCard(background = Color.Transparent, padded = false) {
        Box(
            modifier = Modifier
                .fillMaxWidth()
                .height(260.dp)
                .clip(RoundedCornerShape(36.dp))
                .background(Brush.linearGradient(listOf(Lavender, Color(0xFFFFE0D4), Color(0xFFD7F0E8)))),
            contentAlignment = Alignment.Center,
        ) {
            AuraOrb()
            Column(
                modifier = Modifier
                    .align(Alignment.BottomStart)
                    .padding(24.dp),
            ) {
                Text("Aura of Knowledge", color = Graphite, fontSize = 22.sp, fontWeight = FontWeight.Bold)
                Text("calm, growing, no shame", color = Graphite.copy(alpha = 0.72f))
            }
        }
    }
}

@Composable
private fun AuraOrb() {
    val transition = rememberInfiniteTransition(label = "aura")
    val pulse by transition.animateFloat(
        initialValue = 0.92f,
        targetValue = 1.08f,
        animationSpec = infiniteRepeatable(tween(2600, easing = FastOutSlowInEasing), RepeatMode.Reverse),
        label = "pulse",
    )
    Canvas(
        modifier = Modifier
            .size(178.dp)
            .scale(pulse),
    ) {
        drawCircle(
            brush = Brush.radialGradient(
                listOf(Color.White.copy(alpha = 0.96f), Lavender, Peach.copy(alpha = 0.75f), Mint.copy(alpha = 0.82f)),
                center = center,
                radius = size.minDimension / 1.8f,
            ),
        )
        drawCircle(
            color = Color.White.copy(alpha = 0.42f),
            radius = size.minDimension / 5f,
            center = Offset(center.x - 28.dp.toPx(), center.y - 36.dp.toPx()),
        )
    }
}

@Composable
private fun CandleBadge(days: Int) {
    Row(
        modifier = Modifier
            .clip(RoundedCornerShape(24.dp))
            .background(Color.White.copy(alpha = 0.86f))
            .padding(horizontal = 12.dp, vertical = 8.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Canvas(Modifier.size(22.dp)) {
            val flame = Path().apply {
                moveTo(size.width / 2f, 0f)
                cubicTo(size.width, size.height * 0.4f, size.width * 0.74f, size.height, size.width / 2f, size.height)
                cubicTo(size.width * 0.18f, size.height, 0f, size.height * 0.48f, size.width / 2f, 0f)
            }
            drawPath(flame, Butter)
        }
        Spacer(Modifier.width(6.dp))
        Text("$days", fontWeight = FontWeight.Bold, color = Graphite)
    }
}

@Composable
private fun GrammarNudge() {
    CozyCard(background = Mint.copy(alpha = 0.46f)) {
        Text("Past Simple is tapping the window", fontWeight = FontWeight.Bold, color = Graphite)
        Spacer(Modifier.height(6.dp))
        Text("30 seconds, three tiny quests, zero judgment.", color = InkMuted)
    }
}

@Composable
private fun ConnectionStatus(appState: PajamaAppState) {
    val scope = rememberCoroutineScope()
    when {
        appState.isBooting -> LoadingCard("Connecting")
        appState.errorMessage != null -> CozyCard(background = Peach.copy(alpha = 0.44f)) {
            Text(appState.errorMessage ?: "API is resting.", color = Graphite, fontWeight = FontWeight.Bold)
            Spacer(Modifier.height(10.dp))
            SoftAction(
                text = "Refresh",
                icon = Icons.Rounded.AutoAwesome,
                color = Mint,
                onClick = { scope.launch { appState.refreshAll() } },
            )
        }
        appState.activeBaseUrl != null -> CozyCard(background = Mint.copy(alpha = 0.28f)) {
            Text("Live API connected", color = Graphite, fontWeight = FontWeight.Bold)
        }
    }
}

@Composable
private fun ContextResultCard(
    result: ContextAnalyzeDto,
    isAdding: Boolean,
    onAddAll: () -> Unit,
    onClear: () -> Unit,
) {
    CozyCard(background = Color.White.copy(alpha = 0.76f)) {
        Text(result.summary, color = Graphite, fontWeight = FontWeight.Bold)
        Spacer(Modifier.height(8.dp))
        Text(result.hiddenMeaning, color = InkMuted)
        Spacer(Modifier.height(12.dp))
        result.highlights.take(3).forEach { highlight ->
            Text(highlight.phrase, color = Graphite, fontWeight = FontWeight.Bold)
            Text(highlight.explanation, color = InkMuted)
            Spacer(Modifier.height(8.dp))
        }
        if (result.suggestedWords.isNotEmpty()) {
            Text(result.suggestedWords.take(6).joinToString(" · "), color = Graphite)
            Spacer(Modifier.height(12.dp))
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                SoftAction(
                    text = if (isAdding) "Adding" else "Add words",
                    icon = Icons.Rounded.Bookmarks,
                    color = Peach,
                    modifier = Modifier.weight(1f),
                    enabled = !isAdding,
                    onClick = onAddAll,
                )
                SoftAction(
                    text = "Clear",
                    icon = Icons.Rounded.AutoAwesome,
                    color = Lavender,
                    modifier = Modifier.weight(1f),
                    onClick = onClear,
                )
            }
        }
    }
}

@Composable
private fun LoadingCard(text: String) {
    CozyCard(background = Color.White.copy(alpha = 0.72f)) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            CircularProgressIndicator(modifier = Modifier.size(22.dp), color = Graphite, strokeWidth = 2.dp)
            Spacer(Modifier.width(10.dp))
            Text(text, color = InkMuted, fontWeight = FontWeight.Medium)
        }
    }
}

@Composable
private fun SpeakingRoomsScreen() {
    val appState = LocalPajamaState.current
    val rooms = appState.speakingRooms.map { it.toRoom() }.ifEmpty { fallbackRooms() }
    var activeRoom by remember { mutableStateOf<Room?>(null) }

    ScreenFrame {
        Text("Speaking Rooms", fontSize = 28.sp, fontWeight = FontWeight.Black, color = Graphite)
        ConnectionStatus(appState)
        AnimatedVisibility(activeRoom == null) {
            Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
                rooms.forEach { room ->
                    RoomCard(room = room, onClick = { activeRoom = room })
                }
            }
        }
        AnimatedVisibility(activeRoom != null) {
            DialoguePreview(room = activeRoom ?: rooms.first(), onBack = { activeRoom = null })
        }
    }
}

@Composable
private fun RoomCard(room: Room, onClick: () -> Unit) {
    CozyCard(
        modifier = Modifier.clickable(onClick = onClick),
        background = Color.White.copy(alpha = 0.86f),
    ) {
        Row(verticalAlignment = Alignment.CenterVertically) {
            Box(
                modifier = Modifier
                    .size(58.dp)
                    .clip(CircleShape)
                    .background(room.color.copy(alpha = 0.74f)),
                contentAlignment = Alignment.Center,
            ) {
                Icon(room.icon, contentDescription = null, tint = Graphite)
            }
            Spacer(Modifier.width(14.dp))
            Column(Modifier.weight(1f)) {
                Text(room.title, fontWeight = FontWeight.Bold, fontSize = 19.sp, color = Graphite)
                Text("${room.character} · ${room.vibe}", color = InkMuted, maxLines = 2, overflow = TextOverflow.Ellipsis)
            }
        }
    }
}

@Composable
private fun DialoguePreview(room: Room, onBack: () -> Unit) {
    CozyCard(background = Color.White.copy(alpha = 0.9f)) {
        TextButton(onClick = onBack, contentPadding = androidx.compose.foundation.layout.PaddingValues(0.dp)) {
            Text("Rooms")
        }
        Row(verticalAlignment = Alignment.CenterVertically) {
            Box(
                modifier = Modifier
                    .size(64.dp)
                    .clip(CircleShape)
                    .background(room.color),
                contentAlignment = Alignment.Center,
            ) {
                Icon(room.icon, contentDescription = null, tint = Graphite, modifier = Modifier.size(30.dp))
            }
            Spacer(Modifier.width(14.dp))
            Column {
                Text(room.character, fontWeight = FontWeight.Black, fontSize = 24.sp, color = Graphite)
                Text(room.title, color = InkMuted)
            }
        }
        Spacer(Modifier.height(22.dp))
        ChatBubble("Hey, want to practice a tiny real-life scene?", incoming = true)
        ChatBubble("Yes, but keep it chill.", incoming = false)
        Spacer(Modifier.height(20.dp))
        WaveMicButton()
    }
}

@Composable
private fun ChatBubble(text: String, incoming: Boolean) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        horizontalArrangement = if (incoming) Arrangement.Start else Arrangement.End,
    ) {
        Text(
            text = text,
            modifier = Modifier
                .fillMaxWidth(0.82f)
                .clip(RoundedCornerShape(26.dp))
                .background(if (incoming) Lavender.copy(alpha = 0.72f) else Peach.copy(alpha = 0.72f))
                .padding(16.dp),
            color = Graphite,
        )
    }
    Spacer(Modifier.height(10.dp))
}

@Composable
private fun WaveMicButton() {
    val transition = rememberInfiniteTransition(label = "wave")
    val wave by transition.animateFloat(
        0f,
        1f,
        infiniteRepeatable(tween(1000), RepeatMode.Reverse),
        label = "wave",
    )
    Box(
        modifier = Modifier.fillMaxWidth(),
        contentAlignment = Alignment.Center,
    ) {
        Box(
            modifier = Modifier
                .size(104.dp)
                .clip(CircleShape)
                .background(Brush.radialGradient(listOf(Peach, Lavender))),
            contentAlignment = Alignment.Center,
        ) {
            Canvas(Modifier.fillMaxSize()) {
                repeat(5) { index ->
                    val height = (18 + index * 8 + wave * 16).dp.toPx()
                    drawRoundRect(
                        color = Graphite.copy(alpha = 0.16f + index * 0.05f),
                        topLeft = Offset(size.width / 2 - 28.dp.toPx() + index * 14.dp.toPx(), size.height / 2 - height / 2),
                        size = Size(6.dp.toPx(), height),
                    )
                }
            }
            Icon(Icons.Rounded.Mic, contentDescription = "Hold to speak", tint = Graphite, modifier = Modifier.size(34.dp))
        }
    }
}

@Composable
private fun AddWordCard(
    isAdding: Boolean,
    onAdd: (String) -> Unit,
) {
    var term by remember { mutableStateOf("") }
    CozyCard(background = Lavender.copy(alpha = 0.48f)) {
        Text("New word", fontWeight = FontWeight.Bold, fontSize = 19.sp, color = Graphite)
        Spacer(Modifier.height(10.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalAlignment = Alignment.CenterVertically) {
            OutlinedTextField(
                value = term,
                onValueChange = { term = it },
                modifier = Modifier.weight(1f),
                shape = RoundedCornerShape(24.dp),
                singleLine = true,
                placeholder = { Text("cozy") },
            )
            SoftAction(
                text = if (isAdding) "..." else "Add",
                icon = Icons.Rounded.AutoAwesome,
                color = Mint,
                enabled = !isAdding && term.isNotBlank(),
                onClick = {
                    onAdd(term)
                    term = ""
                },
            )
        }
    }
}

@Composable
private fun StorageScreen() {
    val appState = LocalPajamaState.current
    val scope = rememberCoroutineScope()
    var tab by remember { mutableIntStateOf(0) }

    ScreenFrame {
        Text("My Storage", fontSize = 28.sp, fontWeight = FontWeight.Black, color = Graphite)
        ConnectionStatus(appState)
        AddWordCard(
            isAdding = appState.isAddingWord,
            onAdd = { term -> scope.launch { appState.addWord(term) } },
        )
        TabRow(selectedTabIndex = tab, containerColor = Color.Transparent, contentColor = Graphite) {
            Tab(selected = tab == 0, onClick = { tab = 0 }, text = { Text("My words") })
            Tab(selected = tab == 1, onClick = { tab = 1 }, text = { Text("Review time") })
        }
        if (tab == 0) {
            WordList(
                words = appState.words,
                isLoading = appState.isWordsLoading || appState.isBooting,
                onRefresh = { scope.launch { appState.refreshAll() } },
            )
        } else {
            SrsSwipeCard(
                word = appState.words.firstOrNull(),
                isReviewing = appState.isReviewing,
                onReview = { word, grade -> scope.launch { appState.reviewWord(word, grade) } },
            )
        }
    }
}

@Composable
private fun WordList(
    words: List<WordDto>,
    isLoading: Boolean,
    onRefresh: () -> Unit,
) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        if (isLoading) {
            LoadingCard("Loading words")
        } else if (words.isEmpty()) {
            CozyCard(background = Color.White.copy(alpha = 0.86f)) {
                Text("Storage is waiting for its first word", fontWeight = FontWeight.Bold, color = Graphite)
                Spacer(Modifier.height(10.dp))
                SoftAction("Refresh", Icons.Rounded.AutoAwesome, Mint, onClick = onRefresh)
            }
        } else {
            words.forEach { word ->
                val alpha = 0.28f + word.colorLevel.coerceIn(0, 5) * 0.09f
                CozyCard(background = Lavender.copy(alpha = alpha)) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Column(Modifier.weight(1f)) {
                            Text(word.term, fontSize = 21.sp, fontWeight = FontWeight.Bold, color = Graphite)
                            Text("${word.translation} · ${word.transcription}", color = InkMuted)
                        }
                        Text("${word.colorLevel}/5", color = Graphite, fontWeight = FontWeight.Bold)
                    }
                }
            }
        }
    }
}

@OptIn(ExperimentalFoundationApi::class)
@Composable
private fun SrsSwipeCard(
    word: WordDto?,
    isReviewing: Boolean,
    onReview: (WordDto, ReviewGrade) -> Unit,
) {
    if (word == null) {
        CozyCard(background = Color.White.copy(alpha = 0.86f)) {
            Text("Review deck is calm", fontWeight = FontWeight.Bold, color = Graphite)
            Spacer(Modifier.height(6.dp))
            Text("Add a word and it will show up here.", color = InkMuted)
        }
        return
    }

    var offsetX by remember { mutableFloatStateOf(0f) }
    val trail = if (offsetX >= 0) Mint else Peach
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .height(390.dp),
        contentAlignment = Alignment.Center,
    ) {
        Box(
            modifier = Modifier
                .matchParentSize()
                .clip(RoundedCornerShape(38.dp))
                .background(trail.copy(alpha = (kotlin.math.abs(offsetX) / 500f).coerceIn(0f, 0.42f))),
        )
        CozyCard(
            modifier = Modifier
                .fillMaxWidth(0.92f)
                .aspectRatio(0.78f)
                .offset { IntOffset(offsetX.roundToInt(), 0) }
                .pointerInput(Unit) {
                    detectDragGestures(
                        onDragEnd = {
                            when {
                                offsetX > 140f -> onReview(word, ReviewGrade.Remember)
                                offsetX < -140f -> onReview(word, ReviewGrade.Forgot)
                            }
                            offsetX = 0f
                        },
                        onDrag = { change, dragAmount ->
                            change.consume()
                            offsetX += dragAmount.x
                        },
                    )
                },
            background = Color.White.copy(alpha = 0.94f),
        ) {
            Spacer(Modifier.height(24.dp))
            Text(word.term, fontSize = 38.sp, fontWeight = FontWeight.Black, color = Graphite)
            Spacer(Modifier.height(10.dp))
            Text(word.transcription.ifBlank { word.translation }, color = InkMuted)
            Spacer(Modifier.height(24.dp))
            Text(word.meme.ifBlank { "Swipe right if it stayed. Left if it slipped away." }, color = InkMuted)
            Spacer(Modifier.weight(1f))
            Row(horizontalArrangement = Arrangement.spacedBy(12.dp)) {
                SoftAction(
                    text = "Forgot",
                    icon = Icons.Rounded.Bookmarks,
                    color = Peach,
                    modifier = Modifier.weight(1f),
                    enabled = !isReviewing,
                    onClick = { onReview(word, ReviewGrade.Forgot) },
                )
                SoftAction(
                    text = "Remember",
                    icon = Icons.Rounded.AutoAwesome,
                    color = Mint,
                    modifier = Modifier.weight(1f),
                    enabled = !isReviewing,
                    onClick = { onReview(word, ReviewGrade.Remember) },
                )
            }
        }
    }
}

@Composable
private fun VibeScreen() {
    ScreenFrame {
        Text("Vibe Check", fontSize = 28.sp, fontWeight = FontWeight.Black, color = Graphite)
        CozyCard(background = Color.White.copy(alpha = 0.86f)) {
            Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                Stat("128", "words")
                Stat("46m", "spoken")
                Stat("Chill", "mode")
            }
        }
        CozyCard(background = Lavender.copy(alpha = 0.64f)) {
            Text("AI tone", fontWeight = FontWeight.Bold, fontSize = 20.sp, color = Graphite)
            Spacer(Modifier.height(12.dp))
            listOf("chill-bro from California", "strict British aristocrat", "soft sitcom bestie").forEach { tone ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(22.dp))
                        .background(Color.White.copy(alpha = 0.5f))
                        .padding(14.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Box(
                        Modifier
                            .size(12.dp)
                            .clip(CircleShape)
                            .background(if (tone.startsWith("chill")) Mint else InkMuted.copy(alpha = 0.24f)),
                    )
                    Spacer(Modifier.width(10.dp))
                    Text(tone, color = Graphite)
                }
                Spacer(Modifier.height(8.dp))
            }
        }
    }
}

@Composable
private fun Stat(value: String, label: String) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(value, fontSize = 22.sp, fontWeight = FontWeight.Black, color = Graphite)
        Text(label, color = InkMuted)
    }
}

@Composable
private fun CozyCard(
    modifier: Modifier = Modifier,
    background: Color,
    padded: Boolean = true,
    content: @Composable ColumnScope.() -> Unit,
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        shape = RoundedCornerShape(32.dp),
        colors = CardDefaults.cardColors(containerColor = background),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp),
    ) {
        Column(
            modifier = Modifier.padding(if (padded) 18.dp else 0.dp),
            content = content,
        )
    }
}

@Composable
private fun SoftAction(
    text: String,
    icon: ImageVector,
    color: Color,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    onClick: () -> Unit,
) {
    TextButton(
        onClick = onClick,
        enabled = enabled,
        modifier = modifier
            .height(48.dp)
            .clip(RoundedCornerShape(24.dp))
            .background(color.copy(alpha = if (enabled) 0.72f else 0.32f)),
        colors = ButtonDefaults.textButtonColors(contentColor = Graphite),
    ) {
        Icon(icon, contentDescription = null, modifier = Modifier.size(18.dp))
        Spacer(Modifier.width(8.dp))
        Text(text, fontWeight = FontWeight.Bold, maxLines = 1, overflow = TextOverflow.Ellipsis)
    }
}

private data class Room(
    val title: String,
    val character: String,
    val vibe: String,
    val icon: ImageVector,
    val color: Color,
)

private fun SpeakingRoomDto.toRoom(): Room {
    val lowerId = id.lowercase()
    return when {
        "airport" in lowerId || "gate" in lowerId -> Room(
            title = title,
            character = character,
            vibe = vibe,
            icon = Icons.Rounded.FlightTakeoff,
            color = Mint,
        )
        "interview" in lowerId -> Room(
            title = title,
            character = character,
            vibe = vibe,
            icon = Icons.Rounded.Work,
            color = Lavender,
        )
        else -> Room(
            title = title,
            character = character,
            vibe = vibe,
            icon = Icons.Rounded.Coffee,
            color = Peach,
        )
    }
}

private fun fallbackRooms(): List<Room> = listOf(
    Room("Lo-fi Coffee", "Alex", "barista with soft sarcasm", Icons.Rounded.Coffee, Peach),
    Room("Gate B12", "Nova", "calm airport helper", Icons.Rounded.FlightTakeoff, Mint),
    Room("IT Interview", "Jules", "friendly tech lead", Icons.Rounded.Work, Lavender),
)
