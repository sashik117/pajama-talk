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
import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
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
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.LazyRow
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
import androidx.compose.material.icons.rounded.VolumeUp
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
import androidx.compose.material3.SecondaryTabRow
import androidx.compose.material3.Surface
import androidx.compose.material3.Tab
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
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
import androidx.compose.ui.graphics.vector.ImageVector
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.foundation.text.KeyboardOptions
import cafe.adriel.voyager.navigator.tab.CurrentTab
import cafe.adriel.voyager.navigator.tab.LocalTabNavigator
import cafe.adriel.voyager.navigator.tab.Tab
import cafe.adriel.voyager.navigator.tab.TabNavigator
import cafe.adriel.voyager.navigator.tab.TabOptions
import com.pajamatalk.shared.data.ContextAnalyzeDto
import com.pajamatalk.shared.data.GrammarDropDto
import com.pajamatalk.shared.data.LearningLanguage
import com.pajamatalk.shared.data.NativeLanguage
import com.pajamatalk.shared.data.PajamaAppState
import com.pajamatalk.shared.data.ReviewGrade
import com.pajamatalk.shared.data.SpeakingChatMessage
import com.pajamatalk.shared.data.SpeakingHintsDto
import com.pajamatalk.shared.data.SpeakingRoomDto
import com.pajamatalk.shared.data.SupportedLearningLanguages
import com.pajamatalk.shared.data.SupportedNativeLanguages
import com.pajamatalk.shared.data.VoiceAudioChunkDto
import com.pajamatalk.shared.data.WordDto
import com.pajamatalk.shared.data.nativeLanguageByCode
import com.pajamatalk.shared.platform.PlatformSpeechPlayer
import com.pajamatalk.shared.platform.VoiceRecorderStatus
import com.pajamatalk.shared.platform.rememberPlatformSpeechPlayer
import com.pajamatalk.shared.platform.rememberPlatformVoiceRecorder
import kotlinx.coroutines.launch
import org.jetbrains.compose.resources.DrawableResource
import org.jetbrains.compose.resources.painterResource
import pajamatalk.shared.generated.resources.Res
import pajamatalk.shared.generated.resources.flag_cn
import pajamatalk.shared.generated.resources.flag_cz
import pajamatalk.shared.generated.resources.flag_de
import pajamatalk.shared.generated.resources.flag_es
import pajamatalk.shared.generated.resources.flag_fr
import pajamatalk.shared.generated.resources.flag_gb
import pajamatalk.shared.generated.resources.flag_it
import pajamatalk.shared.generated.resources.flag_jp
import pajamatalk.shared.generated.resources.flag_kr
import pajamatalk.shared.generated.resources.flag_pl
import pajamatalk.shared.generated.resources.flag_pt
import pajamatalk.shared.generated.resources.flag_ru
import pajamatalk.shared.generated.resources.flag_sk
import pajamatalk.shared.generated.resources.flag_tr
import pajamatalk.shared.generated.resources.flag_ua
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
                Box(
                    modifier = Modifier
                        .fillMaxSize()
                        .background(
                            Brush.verticalGradient(
                                listOf(Color(0xFFFFFBFF), Color(0xFFF8F1FF), Color(0xFFFFF4EE)),
                            ),
                        )
                        .imePadding(),
                ) {
                    if (appState.user == null) {
                        AuthScreen(appState)
                    } else {
                        TabNavigator(AuraTab) {
                            Scaffold(
                                contentWindowInsets = WindowInsets(0.dp),
                                bottomBar = { PajamaBottomBar() },
                                containerColor = Color.Transparent,
                            ) { padding ->
                                Box(
                                    modifier = Modifier
                                        .fillMaxSize()
                                        .padding(padding),
                                ) {
                                    CurrentTab()
                                }
                            }
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
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(18.dp),
            contentPadding = androidx.compose.foundation.layout.PaddingValues(top = 18.dp, bottom = 22.dp),
        ) {
            item {
                Column(
                    modifier = Modifier
                        .widthIn(max = 760.dp)
                        .fillMaxWidth(),
                    verticalArrangement = Arrangement.spacedBy(18.dp),
                    content = content,
                )
            }
        }
    }
}

@Composable
private fun AuthScreen(appState: PajamaAppState) {
    val scope = rememberCoroutineScope()
    var isRegister by remember { mutableStateOf(false) }
    var displayName by remember { mutableStateOf("") }
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    val canSubmit = email.trim().length >= 5 && password.length >= 8 && !appState.isAuthenticating && !appState.isBooting

    BoxWithConstraints(
        modifier = Modifier
            .fillMaxSize()
            .statusBarsPadding()
            .navigationBarsPadding(),
    ) {
        val horizontal = if (maxWidth < 420.dp) 18.dp else 32.dp
        LazyColumn(
            modifier = Modifier
                .fillMaxSize()
                .padding(horizontal = horizontal),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(18.dp),
            contentPadding = androidx.compose.foundation.layout.PaddingValues(top = 32.dp, bottom = 32.dp),
        ) {
            item {
                Column(
                    modifier = Modifier
                        .widthIn(max = 560.dp)
                        .fillMaxWidth(),
                    verticalArrangement = Arrangement.spacedBy(18.dp),
                ) {
                    Column {
                        Text("PajamaTalk", fontSize = 34.sp, fontWeight = FontWeight.Bold, color = Graphite)
                        Text("Soft language practice, your pace.", color = InkMuted, fontWeight = FontWeight.Normal)
                    }

                    AuraHero()
                    ConnectionStatus(appState)

                    CozyCard(background = Color.White.copy(alpha = 0.88f)) {
                        Text(
                            if (isRegister) "Create your space" else "Welcome back",
                            fontSize = 22.sp,
                            fontWeight = FontWeight.SemiBold,
                            color = Graphite,
                        )
                        Spacer(Modifier.height(12.dp))
                        AnimatedVisibility(isRegister) {
                            Column {
                                OutlinedTextField(
                                    value = displayName,
                                    onValueChange = { displayName = it },
                                    modifier = Modifier.fillMaxWidth(),
                                    shape = RoundedCornerShape(24.dp),
                                    singleLine = true,
                                    label = { Text("Name") },
                                )
                                Spacer(Modifier.height(10.dp))
                            }
                        }
                        OutlinedTextField(
                            value = email,
                            onValueChange = { email = it },
                            modifier = Modifier.fillMaxWidth(),
                            shape = RoundedCornerShape(24.dp),
                            singleLine = true,
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Email),
                            label = { Text("Email") },
                        )
                        Spacer(Modifier.height(10.dp))
                        OutlinedTextField(
                            value = password,
                            onValueChange = { password = it },
                            modifier = Modifier.fillMaxWidth(),
                            shape = RoundedCornerShape(24.dp),
                            singleLine = true,
                            visualTransformation = PasswordVisualTransformation(),
                            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password),
                            label = { Text("Password") },
                        )
                        Spacer(Modifier.height(14.dp))
                        SoftAction(
                            text = when {
                                appState.isAuthenticating -> "Opening"
                                isRegister -> "Create account"
                                else -> "Log in"
                            },
                            icon = Icons.Rounded.Person,
                            color = Mint,
                            enabled = canSubmit,
                            onClick = {
                                scope.launch {
                                    if (isRegister) {
                                        appState.register(email, password, displayName)
                                    } else {
                                        appState.login(email, password)
                                    }
                                }
                            },
                        )
                        Spacer(Modifier.height(8.dp))
                        TextButton(
                            onClick = { isRegister = !isRegister },
                            enabled = !appState.isAuthenticating,
                            colors = ButtonDefaults.textButtonColors(contentColor = Graphite),
                        ) {
                            Text(if (isRegister) "I already have an account" else "Create a new account")
                        }
                    }

                    CozyCard(background = Lavender.copy(alpha = 0.62f)) {
                        Text("Demo profile", fontWeight = FontWeight.SemiBold, color = Graphite)
                        Spacer(Modifier.height(10.dp))
                        SoftAction(
                            text = if (appState.isAuthenticating) "Opening" else "Continue demo",
                            icon = Icons.Rounded.AutoAwesome,
                            color = Peach,
                            enabled = !appState.isAuthenticating && !appState.isBooting,
                            onClick = { scope.launch { appState.continueAsDemo() } },
                        )
                    }
                }
            }
        }
    }
}

@Composable
private fun AuraScreen() {
    val appState = LocalPajamaState.current
    val scope = rememberCoroutineScope()
    var contextText by remember { mutableStateOf("") }
    var showLanguagePicker by remember { mutableStateOf(false) }

    ScreenFrame {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Column {
                Text("Головна", fontSize = 28.sp, fontWeight = FontWeight.SemiBold, color = Graphite)
                Text(appState.selectedLanguage.label, color = InkMuted, fontSize = 13.sp, fontWeight = FontWeight.Normal)
            }
            LanguageHeaderChip(
                selected = appState.selectedLanguage,
                native = nativeLanguageByCode(appState.user?.nativeLanguageCode ?: "uk"),
                onClick = { showLanguagePicker = !showLanguagePicker },
            )
        }

        ConnectionStatus(appState)
        AnimatedVisibility(showLanguagePicker) {
            LanguagePicker(
                selected = appState.selectedLanguage,
                onSelect = { language ->
                    showLanguagePicker = false
                    scope.launch { appState.selectLanguage(language) }
                },
            )
        }

        CozyCard(background = Color.White.copy(alpha = 0.84f)) {
            Text("Alex is waiting in ${appState.selectedLanguage.label}", fontSize = 21.sp, fontWeight = FontWeight.SemiBold, color = Graphite)
            Spacer(Modifier.height(8.dp))
            Text("One real conversation, zero pressure.", color = InkMuted, fontSize = 13.sp)
            Spacer(Modifier.height(14.dp))
            SoftAction("Enter room", Icons.Rounded.Coffee, Peach, onClick = {})
        }

        appState.learningPath?.let { path ->
            CozyCard(background = Mint.copy(alpha = 0.36f)) {
                Text("${path.languageName}: starter path", fontSize = 20.sp, fontWeight = FontWeight.SemiBold, color = Graphite)
                Spacer(Modifier.height(6.dp))
                Text(path.assistantRole, color = InkMuted, fontSize = 13.sp)
                path.steps.firstOrNull()?.let { step ->
                    Spacer(Modifier.height(12.dp))
                    Text(step.title, color = Graphite, fontWeight = FontWeight.SemiBold)
                    Spacer(Modifier.height(4.dp))
                    Text(step.microTask, color = InkMuted)
                    step.examples.firstOrNull()?.let { phrase ->
                        Spacer(Modifier.height(10.dp))
                        Text(phrase.phrase, color = Graphite, fontWeight = FontWeight.Medium)
                        Text(phrase.meaning, color = InkMuted, fontSize = 13.sp)
                    }
                }
            }
        }

        CozyCard(background = Lavender.copy(alpha = 0.72f)) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(Icons.Rounded.AutoAwesome, contentDescription = null, tint = Graphite)
                Spacer(Modifier.width(10.dp))
                Text("Context Buddy", fontSize = 20.sp, fontWeight = FontWeight.SemiBold, color = Graphite)
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
                    onAddWord = { word -> scope.launch { appState.addWord(word, result.summary) } },
                    onAddAll = { scope.launch { appState.addContextSuggestions() } },
                    onClear = { appState.clearContextResult() },
                )
            }
        }

        GrammarNudge(
            drop = appState.grammarDrops.firstOrNull(),
            isLoading = appState.isGrammarLoading,
        )
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
                Text("Aura of Knowledge", color = Graphite, fontSize = 22.sp, fontWeight = FontWeight.SemiBold)
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
        Text("$days", fontWeight = FontWeight.SemiBold, color = Graphite)
    }
}

@Composable
private fun GrammarNudge(drop: GrammarDropDto?, isLoading: Boolean) {
    val appState = LocalPajamaState.current
    val scope = rememberCoroutineScope()
    if (isLoading && drop == null) {
        LoadingCard("Checking grammar drops")
        return
    }

    val activeDrop = drop ?: GrammarDropDto(
        id = "soft-past-simple",
        title = "Past Simple",
        nudge = "Past Simple is tapping the window for 30 seconds.",
        tinyExplanation = "Finished time, finished action. Keep it small and clean.",
        quests = listOf("I watched it yesterday", "She called me last night", "We met in 2024"),
    )
    val topic = appState.grammarTopics.firstOrNull()
    val exercise = topic?.exercises?.firstOrNull()
    var expanded by remember(activeDrop.id) { mutableStateOf(false) }
    var completedQuest by remember(activeDrop.id) { mutableStateOf<String?>(null) }
    var selectedAnswer by remember(topic?.id, exercise?.id) { mutableStateOf("") }
    var feedback by remember(topic?.id, exercise?.id) { mutableStateOf<String?>(null) }

    CozyCard(background = Mint.copy(alpha = 0.46f)) {
        Text(topic?.title ?: activeDrop.title, fontWeight = FontWeight.SemiBold, color = Graphite)
        Spacer(Modifier.height(6.dp))
        Text(topic?.reason?.ifBlank { activeDrop.nudge } ?: activeDrop.nudge, color = InkMuted)
        AnimatedVisibility(expanded) {
            Column {
                Spacer(Modifier.height(10.dp))
                Text(topic?.microLesson ?: activeDrop.tinyExplanation, color = Graphite, fontWeight = FontWeight.Normal)
                Spacer(Modifier.height(12.dp))
                topic?.rules?.take(3)?.forEach { rule ->
                    Text("• $rule", color = InkMuted, fontSize = 13.sp)
                    Spacer(Modifier.height(6.dp))
                }
                exercise?.let { currentExercise ->
                    Spacer(Modifier.height(8.dp))
                    Text(currentExercise.prompt, color = Graphite, fontWeight = FontWeight.SemiBold)
                    Spacer(Modifier.height(8.dp))
                    currentExercise.options.forEach { option ->
                        val isSelected = selectedAnswer == option
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clip(RoundedCornerShape(20.dp))
                                .background(Color.White.copy(alpha = if (isSelected) 0.82f else 0.46f))
                                .clickable {
                                    selectedAnswer = option
                                    feedback = null
                                }
                                .padding(12.dp),
                            verticalAlignment = Alignment.CenterVertically,
                        ) {
                            Box(
                                Modifier
                                    .size(10.dp)
                                    .clip(CircleShape)
                                    .background(if (isSelected) Mint else InkMuted.copy(alpha = 0.24f)),
                            )
                            Spacer(Modifier.width(10.dp))
                            Text(option, color = Graphite)
                        }
                        Spacer(Modifier.height(8.dp))
                    }
                    SoftAction(
                        text = "Check",
                        icon = Icons.Rounded.AutoAwesome,
                        color = Color.White.copy(alpha = 0.78f),
                        enabled = selectedAnswer.isNotBlank(),
                        onClick = {
                            scope.launch {
                                feedback = appState.checkGrammar(topic.id, currentExercise.id, selectedAnswer)?.feedback
                            }
                        },
                    )
                    feedback?.let {
                        Spacer(Modifier.height(8.dp))
                        Text(it, color = InkMuted, fontSize = 13.sp)
                    }
                    Spacer(Modifier.height(10.dp))
                }
                activeDrop.quests.forEach { quest ->
                    val isDone = completedQuest == quest
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .clip(RoundedCornerShape(20.dp))
                            .background(Color.White.copy(alpha = if (isDone) 0.82f else 0.46f))
                            .clickable { completedQuest = quest }
                            .padding(12.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Box(
                            Modifier
                                .size(10.dp)
                                .clip(CircleShape)
                                .background(if (isDone) Mint else InkMuted.copy(alpha = 0.24f)),
                        )
                        Spacer(Modifier.width(10.dp))
                        Text(quest, color = Graphite, fontWeight = if (isDone) FontWeight.SemiBold else FontWeight.Normal)
                    }
                    Spacer(Modifier.height(8.dp))
                }
            }
        }
        Spacer(Modifier.height(12.dp))
        SoftAction(
            text = if (expanded) "Fold" else "Open drop",
            icon = Icons.Rounded.Psychology,
            color = Color.White.copy(alpha = 0.78f),
            onClick = { expanded = !expanded },
        )
    }
}

@Composable
private fun CodeBadge(code: String, shortLabel: String) {
    Row(verticalAlignment = Alignment.CenterVertically) {
        FlagBadge(code)
        Spacer(Modifier.width(5.dp))
        Text(shortLabel, fontWeight = FontWeight.Medium, fontSize = 12.sp, color = Graphite)
    }
}

@Composable
private fun FlagBadge(code: String) {
    val shape = RoundedCornerShape(5.dp)
    Box(
        modifier = Modifier
            .width(24.dp)
            .height(18.dp)
            .clip(shape)
            .border(1.dp, Graphite.copy(alpha = 0.12f), shape),
    ) {
        Image(
            painter = painterResource(flagResourceForLanguage(code)),
            contentDescription = null,
            contentScale = ContentScale.Crop,
            modifier = Modifier.fillMaxSize(),
        )
    }
}

private fun flagResourceForLanguage(code: String): DrawableResource = when (code) {
    "en" -> Res.drawable.flag_gb
    "uk" -> Res.drawable.flag_ua
    "ru" -> Res.drawable.flag_ru
    "pl" -> Res.drawable.flag_pl
    "sk" -> Res.drawable.flag_sk
    "cs" -> Res.drawable.flag_cz
    "fr" -> Res.drawable.flag_fr
    "es" -> Res.drawable.flag_es
    "it" -> Res.drawable.flag_it
    "de" -> Res.drawable.flag_de
    "pt" -> Res.drawable.flag_pt
    "tr" -> Res.drawable.flag_tr
    "ja" -> Res.drawable.flag_jp
    "ko" -> Res.drawable.flag_kr
    "zh" -> Res.drawable.flag_cn
    else -> Res.drawable.flag_gb
}

@Composable
private fun ConnectionStatus(appState: PajamaAppState) {
    when {
        appState.isBooting -> LoadingCard("Connecting")
        appState.errorMessage != null -> CozyCard(background = Peach.copy(alpha = 0.44f)) {
            Text(appState.errorMessage ?: "API is resting.", color = Graphite, fontWeight = FontWeight.SemiBold)
        }
    }
}

@Composable
private fun LanguageHeaderChip(
    selected: LearningLanguage,
    native: NativeLanguage,
    onClick: () -> Unit,
) {
    TextButton(
        onClick = onClick,
        modifier = Modifier
            .height(42.dp)
            .clip(RoundedCornerShape(24.dp))
            .background(Color.White.copy(alpha = 0.54f))
            .border(1.dp, Color.White.copy(alpha = 0.42f), RoundedCornerShape(24.dp)),
        colors = ButtonDefaults.textButtonColors(contentColor = Graphite),
    ) {
        CodeBadge(selected.code, selected.shortLabel)
        Spacer(Modifier.width(6.dp))
        Text("→", color = InkMuted, fontSize = 12.sp)
        Spacer(Modifier.width(6.dp))
        CodeBadge(native.code, native.shortLabel)
    }
}

@Composable
private fun LanguagePicker(
    selected: LearningLanguage,
    onSelect: (LearningLanguage) -> Unit,
) {
    CozyCard(background = Color.White.copy(alpha = 0.72f)) {
        Text("Learning language", fontWeight = FontWeight.Medium, fontSize = 13.sp, color = InkMuted)
        Spacer(Modifier.height(10.dp))
        LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            items(SupportedLearningLanguages) { language ->
                val isSelected = language.code == selected.code
                TextButton(
                    onClick = { onSelect(language) },
                    modifier = Modifier
                        .height(38.dp)
                        .clip(RoundedCornerShape(22.dp))
                        .background(if (isSelected) Lavender else SoftLilac),
                    colors = ButtonDefaults.textButtonColors(contentColor = Graphite),
                ) {
                    FlagBadge(language.code)
                    Spacer(Modifier.width(6.dp))
                    Text(language.shortLabel, fontWeight = FontWeight.Medium, fontSize = 12.sp)
                }
            }
        }
    }
}

@Composable
private fun NativeLanguagePicker(
    selected: NativeLanguage,
    onSelect: (NativeLanguage) -> Unit,
) {
    CozyCard(background = Color.White.copy(alpha = 0.72f)) {
        Text("Explanation language", fontWeight = FontWeight.Medium, fontSize = 13.sp, color = InkMuted)
        Spacer(Modifier.height(10.dp))
        LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            items(SupportedNativeLanguages) { language ->
                val isSelected = language.code == selected.code
                TextButton(
                    onClick = { onSelect(language) },
                    modifier = Modifier
                        .height(38.dp)
                        .clip(RoundedCornerShape(22.dp))
                        .background(if (isSelected) Mint.copy(alpha = 0.62f) else SoftLilac),
                    colors = ButtonDefaults.textButtonColors(contentColor = Graphite),
                ) {
                    FlagBadge(language.code)
                    Spacer(Modifier.width(6.dp))
                    Text(language.shortLabel, fontWeight = FontWeight.Medium, fontSize = 12.sp)
                }
            }
        }
    }
}

@Composable
private fun ContextResultCard(
    result: ContextAnalyzeDto,
    isAdding: Boolean,
    onAddWord: (String) -> Unit,
    onAddAll: () -> Unit,
    onClear: () -> Unit,
) {
    CozyCard(background = Color.White.copy(alpha = 0.76f)) {
        Text(result.summary, color = Graphite, fontWeight = FontWeight.SemiBold)
        Spacer(Modifier.height(8.dp))
        Text(result.hiddenMeaning, color = InkMuted)
        Spacer(Modifier.height(12.dp))
        result.highlights.take(3).forEach { highlight ->
            Text(highlight.phrase, color = Graphite, fontWeight = FontWeight.SemiBold)
            Text(highlight.explanation, color = InkMuted)
            Spacer(Modifier.height(8.dp))
        }
        if (result.suggestedWords.isNotEmpty()) {
            LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                items(result.suggestedWords.take(8)) { suggested ->
                    TextButton(
                        onClick = { onAddWord(suggested) },
                        enabled = !isAdding,
                        modifier = Modifier
                            .height(42.dp)
                            .clip(RoundedCornerShape(21.dp))
                            .background(Peach.copy(alpha = 0.42f)),
                        colors = ButtonDefaults.textButtonColors(contentColor = Graphite),
                    ) {
                        Icon(Icons.Rounded.Bookmarks, contentDescription = null, modifier = Modifier.size(16.dp))
                        Spacer(Modifier.width(6.dp))
                        Text(suggested, maxLines = 1, overflow = TextOverflow.Ellipsis)
                    }
                }
            }
            Spacer(Modifier.height(8.dp))
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
            Text(text, color = InkMuted, fontWeight = FontWeight.Normal)
        }
    }
}

@Composable
private fun SpeakingRoomsScreen() {
    val appState = LocalPajamaState.current
    val scope = rememberCoroutineScope()
    val rooms = appState.speakingRooms.map { it.toRoom() }.ifEmpty { fallbackRooms() }
    var activeRoom by remember { mutableStateOf<Room?>(null) }
    var pendingRoom by remember { mutableStateOf<Room?>(null) }

    ScreenFrame {
        Text("Speaking Rooms", fontSize = 28.sp, fontWeight = FontWeight.SemiBold, color = Graphite)
        ConnectionStatus(appState)
        AnimatedVisibility(activeRoom == null && pendingRoom == null) {
            Column(verticalArrangement = Arrangement.spacedBy(14.dp)) {
                rooms.forEach { room ->
                    RoomCard(
                        room = room,
                        onClick = {
                            pendingRoom = room
                        },
                    )
                }
            }
        }
        AnimatedVisibility(activeRoom == null && pendingRoom != null) {
            val room = pendingRoom ?: rooms.first()
            MoodGateCard(
                room = room,
                onBack = { pendingRoom = null },
                onMood = { mood ->
                    pendingRoom = null
                    activeRoom = room
                    appState.startSpeakingConversation(composeMoodIntro(room, mood))
                    scope.launch { appState.loadSpeakingHistory(room.id) }
                },
            )
        }
        AnimatedVisibility(activeRoom != null) {
            val room = activeRoom ?: rooms.first()
            DialoguePreview(
                room = room,
                messages = appState.speakingMessages,
                hints = appState.speakingHints,
                isLoadingHints = appState.isLoadingHints,
                isStreaming = appState.isSpeakingStreaming,
                languageCode = appState.selectedLanguage.code,
                onHints = {
                    scope.launch {
                        val lastLine = appState.speakingMessages.lastOrNull { it.incoming }?.text
                        appState.loadSpeakingHints(room.id, lastLine.orEmpty().ifBlank { "I want to keep this conversation going." })
                    }
                },
                onSend = { message -> scope.launch { appState.sendSpeakingMessage(room.id, message) } },
                onVoiceText = { message -> scope.launch { appState.sendVoiceTextMessage(room.id, message) } },
                onVoiceAudio = { chunks, transcriptHint -> scope.launch { appState.sendVoiceAudioMessage(room.id, chunks, transcriptHint) } },
                onBack = {
                    appState.clearSpeakingConversation()
                    activeRoom = null
                    pendingRoom = null
                },
            )
        }
    }
}

@Composable
private fun MoodGateCard(room: Room, onBack: () -> Unit, onMood: (String) -> Unit) {
    CozyCard(background = Color.White.copy(alpha = 0.86f)) {
        TextButton(onClick = onBack, contentPadding = androidx.compose.foundation.layout.PaddingValues(0.dp)) {
            Text("Rooms")
        }
        Text("Mood check", fontSize = 22.sp, fontWeight = FontWeight.SemiBold, color = Graphite)
        Text("${room.character} adapts the first questions to your energy.", color = InkMuted, fontSize = 13.sp)
        Spacer(Modifier.height(10.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            listOf(
                Triple("tired", "🥱", "Soft"),
                Triple("charged", "⚡", "Live"),
                Triple("hard", "🫠", "Kind"),
            ).forEach { (mood, emoji, label) ->
                Column(
                    modifier = Modifier
                        .weight(1f)
                        .clip(RoundedCornerShape(20.dp))
                        .background(Color.White.copy(alpha = 0.58f))
                        .clickable { onMood(mood) }
                        .padding(vertical = 14.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                ) {
                    Text(emoji, fontSize = 26.sp)
                    Text(label, color = Graphite, fontWeight = FontWeight.Medium, fontSize = 12.sp)
                }
            }
        }
    }
}

private fun composeMoodIntro(room: Room, mood: String): String = when (mood) {
    "tired" -> "Low-energy mode. ${room.character} will keep it short, soft, and easy today."
    "charged" -> "Charged mode. ${room.character} will make the pace livelier and a bit more playful."
    "hard" -> "No-pressure mode. ${room.character} will keep the conversation simple and kind."
    else -> room.prompt
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
                    .size(64.dp)
                    .clip(CircleShape)
                    .background(room.color.copy(alpha = 0.74f)),
                contentAlignment = Alignment.Center,
            ) {
                Icon(room.icon, contentDescription = null, tint = Graphite, modifier = Modifier.size(30.dp))
            }
            Spacer(Modifier.width(18.dp))
            Column(Modifier.weight(1f)) {
                Text(room.title, fontWeight = FontWeight.SemiBold, fontSize = 19.sp, color = Graphite)
                Text("${room.character} · ${room.vibe}", color = InkMuted, fontSize = 13.sp, maxLines = 2, overflow = TextOverflow.Ellipsis)
            }
        }
    }
}

@Composable
private fun DialoguePreview(
    room: Room,
    messages: List<SpeakingChatMessage>,
    hints: SpeakingHintsDto?,
    isLoadingHints: Boolean,
    isStreaming: Boolean,
    languageCode: String,
    onHints: () -> Unit,
    onSend: (String) -> Unit,
    onVoiceText: (String) -> Unit,
    onVoiceAudio: (List<VoiceAudioChunkDto>, String) -> Unit,
    onBack: () -> Unit,
) {
    var draft by remember(room.id) { mutableStateOf("") }
    var mode by remember(room.id) { mutableStateOf("text") }

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
                Text(room.character, fontWeight = FontWeight.SemiBold, fontSize = 24.sp, color = Graphite)
                Text(room.title, color = InkMuted)
            }
        }
        Spacer(Modifier.height(14.dp))
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .clip(RoundedCornerShape(22.dp))
                .background(Color.White.copy(alpha = 0.48f))
                .padding(5.dp),
            horizontalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            SpeakingModeChip("Text", Icons.Rounded.Psychology, mode == "text", Modifier.weight(1f)) { mode = "text" }
            SpeakingModeChip("Call", Icons.Rounded.Mic, mode == "call", Modifier.weight(1f)) { mode = "call" }
        }
        Spacer(Modifier.height(14.dp))
        AnimatedVisibility(mode == "call") {
            CallModePreview(
                room = room,
                isStreaming = isStreaming,
                languageCode = languageCode,
                onVoiceText = onVoiceText,
                onVoiceAudio = onVoiceAudio,
                onEndCall = { mode = "text" },
            )
        }
        AnimatedVisibility(mode == "text") {
            Column {
                messages.ifEmpty {
                    listOf(SpeakingChatMessage("Hey, want to practice a tiny real-life scene?", incoming = true))
                }.forEach { message ->
                    ChatBubble(message.text.ifBlank { "..." }, incoming = message.incoming)
                }
                Spacer(Modifier.height(4.dp))
                SoftAction(
                    text = if (isLoadingHints) "Thinking" else "Hints",
                    icon = Icons.Rounded.AutoAwesome,
                    color = Mint,
                    enabled = !isLoadingHints && !isStreaming,
                    onClick = onHints,
                )
                hints?.let { hintSet ->
                    Spacer(Modifier.height(12.dp))
                    HintBubble("Chill", hintSet.simple)
                    HintBubble("Grammar", hintSet.conversational)
                    HintBubble("Question", hintSet.spicy)
                }
                Spacer(Modifier.height(20.dp))
                Row(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalAlignment = Alignment.CenterVertically) {
                    OutlinedTextField(
                        value = draft,
                        onValueChange = { draft = it },
                        modifier = Modifier.weight(1f),
                        shape = RoundedCornerShape(24.dp),
                        singleLine = true,
                        placeholder = { Text("Reply to ${room.character}") },
                    )
                    SoftAction(
                        text = "Call",
                        icon = Icons.Rounded.Mic,
                        color = Mint,
                        enabled = !isStreaming,
                        onClick = { mode = "call" },
                    )
                    SoftAction(
                        text = if (isStreaming) "..." else "Send",
                        icon = Icons.Rounded.AutoAwesome,
                        color = Peach,
                        enabled = !isStreaming && draft.trim().isNotBlank(),
                        onClick = {
                            val message = draft
                            draft = ""
                            onSend(message)
                        },
                    )
                }
            }
        }
    }
}

@Composable
private fun SpeakingModeChip(
    text: String,
    icon: ImageVector,
    selected: Boolean,
    modifier: Modifier = Modifier,
    onClick: () -> Unit,
) {
    TextButton(
        onClick = onClick,
        modifier = modifier
            .height(38.dp)
            .clip(RoundedCornerShape(17.dp))
            .background(if (selected) Lavender.copy(alpha = 0.82f) else Color.Transparent),
        colors = ButtonDefaults.textButtonColors(contentColor = Graphite),
    ) {
        Icon(icon, contentDescription = null, modifier = Modifier.size(17.dp))
        Spacer(Modifier.width(6.dp))
        Text(text, fontWeight = FontWeight.Medium)
    }
}

@Composable
private fun CallModePreview(
    room: Room,
    isStreaming: Boolean,
    languageCode: String,
    onVoiceText: (String) -> Unit,
    onVoiceAudio: (List<VoiceAudioChunkDto>, String) -> Unit,
    onEndCall: () -> Unit,
) {
    val transition = rememberInfiniteTransition(label = "call-aura")
    val pulse by transition.animateFloat(
        0.96f,
        1.04f,
        infiniteRepeatable(tween(1150), RepeatMode.Reverse),
        label = "call-pulse",
    )
    var callDraft by remember(room.id) { mutableStateOf("") }
    val recorder = rememberPlatformVoiceRecorder(languageCode)
    val scope = rememberCoroutineScope()
    val isRecording = recorder.isRecording
    val isProcessing = recorder.status == VoiceRecorderStatus.Processing

    fun toggleRecorder() {
        if (isStreaming || isProcessing) return
        scope.launch {
            if (recorder.isRecording) {
                val recording = recorder.stop()
                if (recording != null && recording.chunks.isNotEmpty()) {
                    onVoiceAudio(recording.chunks, "")
                }
            } else {
                recorder.start()
            }
        }
    }

    Column(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 8.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
    ) {
        Box(
            modifier = Modifier
                .size(220.dp)
                .scale(if (isStreaming || isRecording) pulse else 1f)
                .clip(CircleShape)
                .background(
                    Brush.radialGradient(
                        listOf(Color.White.copy(alpha = 0.9f), Lavender, Peach, Mint),
                    ),
                ),
            contentAlignment = Alignment.Center,
        ) {
            Box(
                modifier = Modifier
                    .size(74.dp)
                    .clip(CircleShape)
                    .background(room.color.copy(alpha = 0.78f)),
                contentAlignment = Alignment.Center,
            ) {
                Icon(room.icon, contentDescription = null, tint = Graphite, modifier = Modifier.size(34.dp))
            }
        }
        Spacer(Modifier.height(14.dp))
        Text(room.character, fontSize = 22.sp, fontWeight = FontWeight.SemiBold, color = Graphite)
        Text(
            when {
                isProcessing -> "Preparing your voice turn..."
                isRecording -> "Recording. Tap the mic again to send."
                recorder.isSupported -> "Tap the mic to speak. Tap again to send."
                else -> "Voice capture is not available in this preview. Use text fallback."
            },
            color = InkMuted,
            fontSize = 13.sp,
        )
        recorder.error?.let { error ->
            Text(
                when (error) {
                    "record-audio-permission-needed" -> "Allow microphone access, then tap the mic again."
                    else -> "Could not record audio. Use the text fallback for this turn."
                },
                color = Graphite.copy(alpha = 0.72f),
                fontSize = 12.sp,
            )
        }
        Spacer(Modifier.height(14.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            listOf("Slow", "Natural", "Fast").forEachIndexed { index, label ->
                Text(
                    label,
                    modifier = Modifier
                        .clip(RoundedCornerShape(16.dp))
                        .background(if (index == 1) Mint.copy(alpha = 0.58f) else Color.White.copy(alpha = 0.58f))
                        .padding(horizontal = 13.dp, vertical = 8.dp),
                    color = Graphite,
                    fontSize = 12.sp,
                    fontWeight = FontWeight.Medium,
                )
            }
        }
        Spacer(Modifier.height(14.dp))
        WaveMicButton(
            active = isRecording,
            enabled = recorder.isSupported && !isStreaming && !isProcessing,
            onClick = ::toggleRecorder,
        )
        Spacer(Modifier.height(12.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalAlignment = Alignment.CenterVertically) {
            OutlinedTextField(
                value = callDraft,
                onValueChange = { callDraft = it },
                modifier = Modifier.weight(1f),
                shape = RoundedCornerShape(22.dp),
                singleLine = true,
                placeholder = { Text("Text fallback for voice") },
            )
            SoftAction(
                text = if (isStreaming) "..." else "Send",
                icon = Icons.Rounded.AutoAwesome,
                color = Peach,
                enabled = !isStreaming && callDraft.trim().isNotBlank(),
                onClick = {
                    val message = callDraft
                    callDraft = ""
                    onVoiceText(message)
                },
            )
        }
        Spacer(Modifier.height(12.dp))
        SoftAction(
            text = "End call",
            icon = Icons.Rounded.Mic,
            color = Peach,
            enabled = true,
            onClick = onEndCall,
        )
    }
}

@Composable
private fun HintBubble(label: String, text: String) {
    Column(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(22.dp))
            .background(Lavender.copy(alpha = 0.42f))
            .padding(14.dp),
    ) {
        Text(label, color = Graphite, fontWeight = FontWeight.SemiBold)
        Spacer(Modifier.height(4.dp))
        Text(text, color = InkMuted)
    }
    Spacer(Modifier.height(8.dp))
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
private fun WaveMicButton(active: Boolean, enabled: Boolean, onClick: () -> Unit) {
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
                .scale(if (active) 0.96f else 1f)
                .clip(CircleShape)
                .background(Brush.radialGradient(if (active) listOf(Mint, Lavender) else listOf(Peach, Lavender)))
                .clickable(enabled = enabled, onClick = onClick),
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
            Icon(
                Icons.Rounded.Mic,
                contentDescription = if (active) "Stop recording" else "Start recording",
                tint = Graphite.copy(alpha = if (enabled) 1f else 0.42f),
                modifier = Modifier.size(34.dp),
            )
        }
    }
}

@Composable
private fun AddWordCard(
    selectedLanguage: LearningLanguage,
    isAdding: Boolean,
    onAdd: (String) -> Unit,
) {
    var term by remember { mutableStateOf("") }
    CozyCard(background = Lavender.copy(alpha = 0.48f)) {
        Text("New word", fontWeight = FontWeight.SemiBold, fontSize = 19.sp, color = Graphite)
        Spacer(Modifier.height(6.dp))
        Text("Add a word or phrase. PajamaTalk will show the translation, examples, and put it into SRS.", color = InkMuted)
        Spacer(Modifier.height(10.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(10.dp), verticalAlignment = Alignment.CenterVertically) {
            OutlinedTextField(
                value = term,
                onValueChange = { term = it },
                modifier = Modifier.weight(1f),
                shape = RoundedCornerShape(24.dp),
                singleLine = true,
                placeholder = { Text(selectedLanguage.sampleWord) },
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
    val speech = rememberPlatformSpeechPlayer(appState.selectedLanguage.code)
    var tab by remember { mutableIntStateOf(0) }
    var lastAdded by remember { mutableStateOf<WordDto?>(null) }

    ScreenFrame {
        Text("My Storage", fontSize = 28.sp, fontWeight = FontWeight.SemiBold, color = Graphite)
        ConnectionStatus(appState)
        LanguagePicker(
            selected = appState.selectedLanguage,
            onSelect = { language -> scope.launch { appState.selectLanguage(language) } },
        )
        AddWordCard(
            selectedLanguage = appState.selectedLanguage,
            isAdding = appState.isAddingWord,
            onAdd = { term -> scope.launch { lastAdded = appState.addWord(term) } },
        )
        lastAdded?.let { word ->
            CozyCard(background = Mint.copy(alpha = 0.28f)) {
                Text("Added to dictionary", color = InkMuted)
                Spacer(Modifier.height(6.dp))
                Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text(word.term, modifier = Modifier.weight(1f), fontSize = 20.sp, fontWeight = FontWeight.SemiBold, color = Graphite)
                    ListenAction(word.term, appState.selectedLanguage.code, speech)
                }
                Text(word.translation, color = Graphite, fontWeight = FontWeight.Medium)
                PronunciationText(word.transcription)
                Spacer(Modifier.height(8.dp))
                ListeningLine(word.exampleOne, appState.selectedLanguage.code, speech)
            }
        }
        SecondaryTabRow(selectedTabIndex = tab, containerColor = Color.Transparent, contentColor = Graphite) {
            Tab(selected = tab == 0, onClick = { tab = 0 }, text = { Text("My words") })
            Tab(selected = tab == 1, onClick = { tab = 1 }, text = { Text("Review time") })
        }
        if (tab == 0) {
            WordList(
                words = appState.words,
                isLoading = appState.isWordsLoading || appState.isBooting,
                languageCode = appState.selectedLanguage.code,
                speech = speech,
            )
        } else {
            SrsSwipeCard(
                word = appState.dueWords.firstOrNull(),
                isLoading = appState.isDueWordsLoading,
                isReviewing = appState.isReviewing,
                languageCode = appState.selectedLanguage.code,
                speech = speech,
                onReview = { word, grade -> scope.launch { appState.reviewWord(word, grade) } },
            )
        }
    }
}

@Composable
private fun ListenAction(
    text: String,
    languageCode: String,
    speech: PlatformSpeechPlayer,
    modifier: Modifier = Modifier,
) {
    TextButton(
        onClick = { speech.speak(text, languageCode) },
        enabled = speech.isSupported && text.isNotBlank(),
        modifier = modifier
            .size(34.dp)
            .clip(CircleShape)
            .background(Mint.copy(alpha = 0.46f)),
        colors = ButtonDefaults.textButtonColors(contentColor = Graphite),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(0.dp),
    ) {
        Icon(Icons.Rounded.VolumeUp, contentDescription = "Listen", modifier = Modifier.size(17.dp))
    }
}

@Composable
private fun ListeningLine(
    text: String,
    languageCode: String,
    speech: PlatformSpeechPlayer,
) {
    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        Text(text, modifier = Modifier.weight(1f), color = InkMuted)
        ListenAction(text, languageCode, speech)
    }
}

@Composable
private fun PronunciationText(value: String) {
    if (value.isBlank()) return
    Row(
        modifier = Modifier
            .clip(RoundedCornerShape(999.dp))
            .background(Color.White.copy(alpha = 0.56f))
            .padding(horizontal = 9.dp, vertical = 5.dp),
        horizontalArrangement = Arrangement.spacedBy(7.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        Text("How to say", color = InkMuted, fontSize = 10.sp, fontWeight = FontWeight.SemiBold)
        Text(value, color = Graphite, fontSize = 12.sp, fontWeight = FontWeight.SemiBold)
    }
}

@Composable
private fun WordList(
    words: List<WordDto>,
    isLoading: Boolean,
    languageCode: String,
    speech: PlatformSpeechPlayer,
) {
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        if (isLoading) {
            LoadingCard("Loading words")
        } else if (words.isEmpty()) {
            CozyCard(background = Color.White.copy(alpha = 0.86f)) {
                Text("Storage is waiting for its first word", fontWeight = FontWeight.SemiBold, color = Graphite)
                Spacer(Modifier.height(10.dp))
                Text("Add a word above to start your storage.", color = InkMuted)
            }
        } else {
            words.forEach { word ->
                var expanded by remember(word.id) { mutableStateOf(false) }
                val alpha = 0.28f + word.colorLevel.coerceIn(0, 5) * 0.09f
                CozyCard(
                    modifier = Modifier.clickable { expanded = !expanded },
                    background = Lavender.copy(alpha = alpha),
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Column(Modifier.weight(1f)) {
                            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                                Text(word.term, modifier = Modifier.weight(1f), fontSize = 21.sp, fontWeight = FontWeight.SemiBold, color = Graphite)
                                ListenAction(word.term, languageCode, speech)
                            }
                            Text(word.translation, color = InkMuted)
                            PronunciationText(word.transcription)
                        }
                        Text("${word.colorLevel}/5", color = Graphite, fontWeight = FontWeight.Medium)
                    }
                    AnimatedVisibility(expanded) {
                        Column {
                            Spacer(Modifier.height(12.dp))
                            Text(word.meme.ifBlank { "No meme yet, but the word has entered storage." }, color = Graphite)
                            Spacer(Modifier.height(10.dp))
                            ListeningLine(word.exampleOne, languageCode, speech)
                            Spacer(Modifier.height(6.dp))
                            ListeningLine(word.exampleTwo, languageCode, speech)
                        }
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
    isLoading: Boolean,
    isReviewing: Boolean,
    languageCode: String,
    speech: PlatformSpeechPlayer,
    onReview: (WordDto, ReviewGrade) -> Unit,
) {
    if (isLoading) {
        LoadingCard("Loading review deck")
        return
    }

    if (word == null) {
        CozyCard(background = Color.White.copy(alpha = 0.86f)) {
            Text("Review deck is calm", fontWeight = FontWeight.SemiBold, color = Graphite)
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
            Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(10.dp)) {
                Text(word.term, modifier = Modifier.weight(1f), fontSize = 38.sp, fontWeight = FontWeight.SemiBold, color = Graphite)
                ListenAction(word.term, languageCode, speech)
            }
            Spacer(Modifier.height(10.dp))
            PronunciationText(word.transcription.ifBlank { word.translation })
            Spacer(Modifier.height(24.dp))
            Text(word.meme.ifBlank { "Swipe right if it stayed. Left if it slipped away." }, color = InkMuted)
            Spacer(Modifier.height(10.dp))
            ListeningLine(word.exampleOne, languageCode, speech)
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
    val appState = LocalPajamaState.current
    val scope = rememberCoroutineScope()
    val user = appState.user
    val nativeCode = user?.nativeLanguageCode ?: "en"
    val vibeModes = listOf("Chill" to 5, "Normal" to 15, "Hardcore" to 30)
    val tones = listOf("Neutral teacher", "Supportive coach", "Precise examiner")
    val currentLevels = listOf("Starter", "A1", "A2", "B1", "B2", "C1")
    val targetLevels = listOf("A1", "A2", "B1", "B2", "C1", "Fluent")
    val effortLevels = listOf("Light", "Steady", "Intense")

    ScreenFrame {
        Text("Vibe Check", fontSize = 28.sp, fontWeight = FontWeight.SemiBold, color = Graphite)
        ConnectionStatus(appState)
        CozyCard(background = Color.White.copy(alpha = 0.86f)) {
            Row(horizontalArrangement = Arrangement.SpaceBetween, modifier = Modifier.fillMaxWidth()) {
                Stat("${appState.stats?.languageWords ?: appState.words.size}", "words")
                Stat("${appState.stats?.dueReviews ?: 0}", "due")
                Stat(appState.selectedLanguage.shortLabel, "language")
            }
        }
        LanguagePicker(
            selected = appState.selectedLanguage,
            onSelect = { language -> scope.launch { appState.selectLanguage(language) } },
        )
        NativeLanguagePicker(
            selected = nativeLanguageByCode(user?.nativeLanguageCode ?: "uk"),
            onSelect = { language -> scope.launch { appState.selectNativeLanguage(language) } },
        )
        CozyCard(background = Color.White.copy(alpha = 0.58f)) {
            Text(profileLabel(nativeCode, "Learning profile"), fontWeight = FontWeight.SemiBold, color = Graphite)
            Spacer(Modifier.height(10.dp))
            ProfileOptionRow(
                title = profileLabel(nativeCode, "Current level"),
                selected = user?.currentLevel ?: "Starter",
                options = currentLevels,
                nativeCode = nativeCode,
                onSelect = { level -> scope.launch { appState.setCurrentLevel(level) } },
            )
            ProfileOptionRow(
                title = profileLabel(nativeCode, "Goal level"),
                selected = user?.targetLevel ?: "B1",
                options = targetLevels,
                nativeCode = nativeCode,
                onSelect = { level -> scope.launch { appState.setTargetLevel(level) } },
            )
            ProfileOptionRow(
                title = profileLabel(nativeCode, "Effort"),
                selected = user?.effortLevel ?: "Steady",
                options = effortLevels,
                nativeCode = nativeCode,
                onSelect = { level -> scope.launch { appState.setEffortLevel(level) } },
            )
        }
        CozyCard(background = Mint.copy(alpha = 0.42f)) {
            Text("Vibe mode", fontWeight = FontWeight.SemiBold, fontSize = 20.sp, color = Graphite)
            Spacer(Modifier.height(12.dp))
            vibeModes.forEach { (mode, _) ->
                val selected = user?.learningVibe == mode
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(22.dp))
                        .background(Color.White.copy(alpha = if (selected) 0.78f else 0.42f))
                        .clickable { scope.launch { appState.setLearningVibe(mode) } }
                        .padding(14.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Box(
                        Modifier
                            .size(12.dp)
                            .clip(CircleShape)
                            .background(if (selected) Mint else InkMuted.copy(alpha = 0.24f)),
                    )
                    Spacer(Modifier.width(10.dp))
                    Text(profileLabel(nativeCode, mode), color = Graphite, fontWeight = if (selected) FontWeight.SemiBold else FontWeight.Normal)
                }
                Spacer(Modifier.height(8.dp))
            }
        }
        CozyCard(background = Lavender.copy(alpha = 0.64f)) {
            Text("AI tone", fontWeight = FontWeight.SemiBold, fontSize = 20.sp, color = Graphite)
            Spacer(Modifier.height(12.dp))
            tones.forEach { tone ->
                val selected = user?.aiTone == tone
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clip(RoundedCornerShape(22.dp))
                        .background(Color.White.copy(alpha = if (selected) 0.78f else 0.5f))
                        .clickable { scope.launch { appState.setAiTone(tone) } }
                        .padding(14.dp),
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Box(
                        Modifier
                            .size(12.dp)
                            .clip(CircleShape)
                            .background(if (selected) Mint else InkMuted.copy(alpha = 0.24f)),
                    )
                    Spacer(Modifier.width(10.dp))
                    Text(profileLabel(nativeCode, tone), color = Graphite, fontWeight = if (selected) FontWeight.SemiBold else FontWeight.Normal)
                }
                Spacer(Modifier.height(8.dp))
            }
        }
        CozyCard(background = Peach.copy(alpha = 0.34f)) {
            Text(user?.displayName ?: "Dreamer", fontWeight = FontWeight.SemiBold, color = Graphite)
            Spacer(Modifier.height(12.dp))
            SoftAction(
                text = "Log out",
                icon = Icons.Rounded.Person,
                color = Color.White.copy(alpha = 0.7f),
                onClick = { appState.logout() },
            )
            Spacer(Modifier.height(6.dp))
            Text("Native: ${(user?.nativeLanguageCode ?: "uk").uppercase()} · ${user?.email ?: "dev user"}", color = InkMuted)
        }
    }
}

@Composable
private fun ProfileOptionRow(
    title: String,
    selected: String,
    options: List<String>,
    nativeCode: String,
    onSelect: (String) -> Unit,
) {
    Text(title, color = InkMuted, fontSize = 13.sp, fontWeight = FontWeight.Medium)
    Spacer(Modifier.height(6.dp))
    LazyRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
        items(options) { option ->
            val isSelected = option == selected
            TextButton(
                onClick = { onSelect(option) },
                modifier = Modifier
                    .height(36.dp)
                    .clip(RoundedCornerShape(18.dp))
                    .background(if (isSelected) Mint.copy(alpha = 0.68f) else SoftLilac),
                colors = ButtonDefaults.textButtonColors(contentColor = Graphite),
            ) {
                Text(profileLabel(nativeCode, option), fontWeight = if (isSelected) FontWeight.SemiBold else FontWeight.Normal, fontSize = 12.sp)
            }
        }
    }
    Spacer(Modifier.height(10.dp))
}

private fun profileLabel(nativeCode: String, key: String): String {
    val uk = mapOf(
        "Learning profile" to "Профіль навчання",
        "Current level" to "Поточний рівень",
        "Goal level" to "Цільовий рівень",
        "Effort" to "Зусилля",
        "Starter" to "З нуля",
        "Fluent" to "Вільно",
        "Light" to "Легко",
        "Steady" to "Стабільно",
        "Intense" to "Інтенсивно",
        "Chill" to "Спокійно",
        "Normal" to "Нормально",
        "Hardcore" to "Потужно",
        "Neutral teacher" to "Нейтральний вчитель",
        "Supportive coach" to "Підтримуючий коуч",
        "Precise examiner" to "Точний екзаменатор",
    )
    val ru = mapOf(
        "Learning profile" to "Профиль обучения",
        "Current level" to "Текущий уровень",
        "Goal level" to "Целевой уровень",
        "Effort" to "Усилия",
        "Starter" to "С нуля",
        "Fluent" to "Свободно",
        "Light" to "Легко",
        "Steady" to "Стабильно",
        "Intense" to "Интенсивно",
        "Chill" to "Спокойно",
        "Normal" to "Нормально",
        "Hardcore" to "Мощно",
        "Neutral teacher" to "Нейтральный учитель",
        "Supportive coach" to "Поддерживающий коуч",
        "Precise examiner" to "Точный экзаменатор",
    )
    return when (nativeCode) {
        "uk" -> uk[key]
        "ru" -> ru[key]
        else -> null
    } ?: key
}

@Composable
private fun Stat(value: String, label: String) {
    Column(horizontalAlignment = Alignment.CenterHorizontally) {
        Text(value, fontSize = 22.sp, fontWeight = FontWeight.SemiBold, color = Graphite)
        Text(label, color = InkMuted, fontSize = 12.sp, fontWeight = FontWeight.Normal)
    }
}

@Composable
private fun CozyCard(
    modifier: Modifier = Modifier,
    background: Color,
    padded: Boolean = true,
    content: @Composable ColumnScope.() -> Unit,
) {
    val shape = RoundedCornerShape(28.dp)
    val glassBackground = if (background == Color.Transparent) {
        background
    } else {
        background.copy(alpha = background.alpha.coerceAtMost(0.62f))
    }
    Card(
        modifier = modifier
            .fillMaxWidth()
            .border(1.dp, Color.White.copy(alpha = 0.42f), shape),
        shape = shape,
        colors = CardDefaults.cardColors(containerColor = glassBackground),
        elevation = CardDefaults.cardElevation(defaultElevation = 0.dp),
    ) {
        Column(
            modifier = Modifier.padding(if (padded) 16.dp else 0.dp),
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
            .height(42.dp)
            .clip(RoundedCornerShape(21.dp))
            .background(color.copy(alpha = if (enabled) 0.72f else 0.32f)),
        colors = ButtonDefaults.textButtonColors(contentColor = Graphite),
    ) {
        Icon(icon, contentDescription = null, modifier = Modifier.size(18.dp))
        Spacer(Modifier.width(8.dp))
        Text(text, fontWeight = FontWeight.Medium, maxLines = 1, overflow = TextOverflow.Ellipsis)
    }
}

private data class Room(
    val id: String,
    val title: String,
    val character: String,
    val vibe: String,
    val prompt: String,
    val icon: ImageVector,
    val color: Color,
)

private fun SpeakingRoomDto.toRoom(): Room {
    val lowerId = id.lowercase()
    return when {
        "airport" in lowerId || "gate" in lowerId -> Room(
            id = id,
            title = title,
            character = character,
            vibe = vibe,
            prompt = prompt,
            icon = Icons.Rounded.FlightTakeoff,
            color = Mint,
        )
        "interview" in lowerId -> Room(
            id = id,
            title = title,
            character = character,
            vibe = vibe,
            prompt = prompt,
            icon = Icons.Rounded.Work,
            color = Lavender,
        )
        "market" in lowerId -> Room(
            id = id,
            title = title,
            character = character,
            vibe = vibe,
            prompt = prompt,
            icon = Icons.Rounded.Bookmarks,
            color = Butter,
        )
        "doctor" in lowerId || "street" in lowerId -> Room(
            id = id,
            title = title,
            character = character,
            vibe = vibe,
            prompt = prompt,
            icon = Icons.Rounded.Psychology,
            color = Mint,
        )
        "date" in lowerId || "campus" in lowerId -> Room(
            id = id,
            title = title,
            character = character,
            vibe = vibe,
            prompt = prompt,
            icon = Icons.Rounded.AutoAwesome,
            color = Peach,
        )
        else -> Room(
            id = id,
            title = title,
            character = character,
            vibe = vibe,
            prompt = prompt,
            icon = Icons.Rounded.Coffee,
            color = Peach,
        )
    }
}

private fun fallbackRooms(): List<Room> = listOf(
    Room("coffee-alex", "Lo-fi Coffee", "Alex", "barista with soft sarcasm", "Teacher mode. Say one tiny line.", Icons.Rounded.Coffee, Peach),
    Room("airport-nova", "Gate B12", "Nova", "calm airport helper", "Teacher mode. Ask for help.", Icons.Rounded.FlightTakeoff, Mint),
    Room("interview-jules", "IT Interview", "Jules", "friendly tech lead", "Teacher mode. Introduce yourself.", Icons.Rounded.Work, Lavender),
    Room("market-mia", "Tiny Market", "Mia", "patient shop assistant", "Teacher mode. Ask for a price.", Icons.Rounded.Bookmarks, Butter),
    Room("street-ivy", "City Directions", "Ivy", "helpful local guide", "Teacher mode. Ask where to go.", Icons.Rounded.Psychology, Mint),
)
