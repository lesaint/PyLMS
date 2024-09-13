package fr.javatronic.lms.core

enum class Sex {
    MALE,
    FEMALE,
    UNSET
}

data class PersonId(val id: Int)

data class Person(val id: PersonId, val firstname: String, val lastname: String?, val sex: Sex)

data class PersonMetadata(val person: Person, val created: Long)

class PersonIdGenerator(private var nextId: Int = 1, persons: List<Person>) {
    init {
        if (persons.isNotEmpty()) {
            this.nextId = persons.maxOf { it.id.id } + 1
        }
    }

    fun nextPersonId(): Int {
        val res = nextId
        nextId += 1
        return res
    }
}