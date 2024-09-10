package fr.javatronic.lms.android

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Clear
import androidx.compose.material3.BottomAppBar
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import fr.javatronic.lms.android.ui.theme.AndroLMSTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            AndroLMSTheme {
                ScaffoldExample()
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ScaffoldExample() {
    var persons by remember { mutableStateOf(searchPersons("")) }
    var searchQuery by remember { mutableStateOf("") }

    Scaffold(topBar = {
        TopAppBar(colors = TopAppBarDefaults.topAppBarColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer,
            titleContentColor = MaterialTheme.colorScheme.primary
        ), title = {
            Text("AndroLMS")
        })
    }, bottomBar = {
        BottomAppBar(
            containerColor = MaterialTheme.colorScheme.primaryContainer,
            contentColor = MaterialTheme.colorScheme.primary,
        ) {
            Text(
                modifier = Modifier.fillMaxWidth(),
                textAlign = TextAlign.Center,
                text = if (searchQuery.isNotEmpty()) "Searching for ${searchQuery}..." else "Displaying everything",
            )
        }
//    }, floatingActionButton = {
//        FloatingActionButton(onClick = { }) {
//            Icon(Icons.Default.Add, contentDescription = "Create person")
//        }
    }) { innerPadding ->
        PersonsList(
            persons = persons,
            searchQuery = searchQuery,
            onSearchStringChange = { text: String ->
                searchQuery = text
                persons = searchPersons(text)
            },
            modifier = Modifier.padding(innerPadding)
        )
    }
}


data class Person(val id: Int, val firstname: String, val lastname: String?)

@Composable
fun PersonsList(
    persons: List<Person>,
    searchQuery: String,
    onSearchStringChange: (String) -> Unit,
    modifier: Modifier
) {
    Column(modifier = modifier) {
        SearchField(searchQuery, onSearchStringChange)
        LazyColumn(
            modifier = Modifier.padding(
                start = 0.dp,
                end = 0.dp,
                top = 10.dp,
                bottom = 0.dp
            )
        ) {
            items(persons) { item: Person -> PersonView(item) }
        }
    }
}

@Composable
fun SearchField(searchQuery: String, onSearchStringChange: (String) -> Unit) {
    var localText by remember { mutableStateOf(searchQuery) }
    // source: https://stackoverflow.com/a/63696027
    val keyboardController = LocalSoftwareKeyboardController.current

    OutlinedTextField(
        value = localText,
        onValueChange = { localText = it },
        label = { Text("Search") },
        modifier = Modifier.fillMaxWidth(),
        singleLine = true,
        keyboardOptions = KeyboardOptions(imeAction = ImeAction.Search),
        keyboardActions = KeyboardActions(onSearch = {
            keyboardController?.hide()
            onSearchStringChange(localText)
        }),
        trailingIcon = {
            // source: https://stackoverflow.com/a/68483797 and https://stackoverflow.com/a/71887430
            when {
                localText.isNotEmpty() -> Icon(Icons.Default.Clear,
                    contentDescription = "clear search",
                    modifier = Modifier.clickable {
                        keyboardController?.hide()
                        localText = ""
                        onSearchStringChange("")
                    }
                )
            }
        }
    )
}

@Composable
fun PersonView(person: Person) {
    Card(modifier = Modifier.padding(5.dp)) {
        val lastname = if (person.lastname != null) " " + person.lastname else ""
        Text(
            text = "(${person.id}) ${person.firstname}${lastname}",
            modifier = Modifier.fillMaxWidth()
        )
    }
}

@Preview(showBackground = true)
@Composable
fun PersonsListPreview() {
    AndroLMSTheme {
        var persons by remember { mutableStateOf(searchPersons("")) }
        var searchQuery by remember { mutableStateOf("") }

        val onSearchStringChange: (String) -> Unit = { text: String ->
            searchQuery = text
            persons = searchPersons(text)
        }
        PersonsList(
            persons = persons,
            searchQuery = searchQuery,
            onSearchStringChange = onSearchStringChange,
            modifier = Modifier.padding()
        )
    }
}

private fun searchPersons(text: String): List<Person> {
    val p = (1..30).map { Person(it, "fn${it}", if (it % 2 == 0) "ln${it}" else null) }
    return p.filter { it.firstname.contains(text) }
}