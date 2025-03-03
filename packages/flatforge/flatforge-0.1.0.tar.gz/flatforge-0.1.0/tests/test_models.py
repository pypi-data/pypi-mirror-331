"""
Tests for the models module.
"""
import unittest
from flatforge.models import Rule, GlobalRule, Section, FileProperties, RuleResult
from flatforge.models import Message, MessageSeverity


class TestRule(unittest.TestCase):
    """Tests for the Rule class."""
    
    def test_init(self):
        """Test initialization of Rule."""
        rule = Rule(name="required", parameters=["param1", "param2"], column_alias="alias", is_optional=True)
        
        self.assertEqual(rule.name, "required")
        self.assertEqual(rule.parameters, ["param1", "param2"])
        self.assertEqual(rule.column_alias, "alias")
        self.assertTrue(rule.is_optional)
    
    def test_init_defaults(self):
        """Test initialization of Rule with default values."""
        rule = Rule(name="required")
        
        self.assertEqual(rule.name, "required")
        self.assertEqual(rule.parameters, [])
        self.assertIsNone(rule.column_alias)
        self.assertFalse(rule.is_optional)
    
    def test_str(self):
        """Test string representation of Rule."""
        rule = Rule(name="required", parameters=["param1", "param2"], column_alias="alias", is_optional=True)
        
        self.assertIn("required", str(rule))
        self.assertIn("param1", str(rule))
        self.assertIn("param2", str(rule))
        self.assertIn("alias", str(rule))
        self.assertIn("optional", str(rule))


class TestGlobalRule(unittest.TestCase):
    """Tests for the GlobalRule class."""
    
    def test_init(self):
        """Test initialization of GlobalRule."""
        rule = GlobalRule(
            name="cr_unique",
            parameters=["param1", "param2"],
            section_index="1",
            column_index=2,
            column_alias="alias",
            is_optional=True
        )
        
        self.assertEqual(rule.name, "cr_unique")
        self.assertEqual(rule.parameters, ["param1", "param2"])
        self.assertEqual(rule.section_index, "1")
        self.assertEqual(rule.column_index, 2)
        self.assertEqual(rule.column_alias, "alias")
        self.assertTrue(rule.is_optional)
    
    def test_init_defaults(self):
        """Test initialization of GlobalRule with default values."""
        rule = GlobalRule(name="cr_unique", section_index="1", column_index=2)
        
        self.assertEqual(rule.name, "cr_unique")
        self.assertEqual(rule.parameters, [])
        self.assertEqual(rule.section_index, "1")
        self.assertEqual(rule.column_index, 2)
        self.assertIsNone(rule.column_alias)
        self.assertFalse(rule.is_optional)
    
    def test_str(self):
        """Test string representation of GlobalRule."""
        rule = GlobalRule(
            name="cr_unique",
            parameters=["param1", "param2"],
            section_index="1",
            column_index=2,
            column_alias="alias",
            is_optional=True
        )
        
        self.assertIn("cr_unique", str(rule))
        self.assertIn("param1", str(rule))
        self.assertIn("param2", str(rule))
        self.assertIn("section_index=1", str(rule))
        self.assertIn("column_index=2", str(rule))
        self.assertIn("alias", str(rule))
        self.assertIn("optional", str(rule))


class TestSection(unittest.TestCase):
    """Tests for the Section class."""
    
    def test_init(self):
        """Test initialization of Section."""
        section = Section(
            index="1",
            section_format="fl{10,5,15}",
            length=30,
            rules={0: [Rule(name="required")], 1: [Rule(name="numeric")]},
            instructions=[Rule(name="instruction1")]
        )
        
        self.assertEqual(section.index, "1")
        self.assertEqual(section.section_format, "fl{10,5,15}")
        self.assertEqual(section.length, 30)
        self.assertEqual(len(section.rules), 2)
        self.assertEqual(len(section.instructions), 1)
    
    def test_init_defaults(self):
        """Test initialization of Section with default values."""
        section = Section(index="1")
        
        self.assertEqual(section.index, "1")
        self.assertIsNone(section.section_format)
        self.assertEqual(section.length, 0)
        self.assertEqual(section.rules, {})
        self.assertEqual(section.instructions, [])
    
    def test_str(self):
        """Test string representation of Section."""
        section = Section(
            index="1",
            section_format="fl{10,5,15}",
            length=30,
            rules={0: [Rule(name="required")], 1: [Rule(name="numeric")]},
            instructions=[Rule(name="instruction1")]
        )
        
        self.assertIn("Section 1", str(section))
        self.assertIn("fl{10,5,15}", str(section))
        self.assertIn("length=30", str(section))


class TestFileProperties(unittest.TestCase):
    """Tests for the FileProperties class."""
    
    def test_init(self):
        """Test initialization of FileProperties."""
        metadata = FileProperties()
        
        self.assertEqual(metadata.parameters, {})
        self.assertEqual(metadata.sections, {})
        self.assertEqual(metadata.global_rules, [])
    
    def test_set_parameters(self):
        """Test setting parameters."""
        metadata = FileProperties()
        metadata.set_parameters({"key1": "value1", "key2": "value2"})
        
        self.assertEqual(metadata.parameters["key1"], "value1")
        self.assertEqual(metadata.parameters["key2"], "value2")
    
    def test_get_parameter(self):
        """Test getting parameters."""
        metadata = FileProperties()
        metadata.set_parameters({"key1": "value1", "key2": "value2"})
        
        self.assertEqual(metadata.get_parameter("key1"), "value1")
        self.assertEqual(metadata.get_parameter("key2"), "value2")
        self.assertEqual(metadata.get_parameter("key3", "default"), "default")
    
    def test_get_section(self):
        """Test getting sections."""
        metadata = FileProperties()
        section = Section(index="1")
        metadata.sections = {"1": section}
        
        self.assertEqual(metadata.get_section("1"), section)
        self.assertIsNone(metadata.get_section("2"))


class TestRuleResult(unittest.TestCase):
    """Tests for the RuleResult class."""
    
    def test_init(self):
        """Test initialization of RuleResult."""
        rule = Rule(name="required")
        message = Message(text="Error message", section_index="1", column_index=2)
        
        result = RuleResult(rule=rule, value="test", is_valid=False, message=message)
        
        self.assertEqual(result.rule, rule)
        self.assertEqual(result.value, "test")
        self.assertFalse(result.is_valid)
        self.assertEqual(result.message, message)
    
    def test_init_defaults(self):
        """Test initialization of RuleResult with default values."""
        rule = Rule(name="required")
        
        result = RuleResult(rule=rule, value="test")
        
        self.assertEqual(result.rule, rule)
        self.assertEqual(result.value, "test")
        self.assertTrue(result.is_valid)
        self.assertIsNone(result.message)
    
    def test_str(self):
        """Test string representation of RuleResult."""
        rule = Rule(name="required")
        message = Message(text="Error message", section_index="1", column_index=2)
        
        result = RuleResult(rule=rule, value="test", is_valid=False, message=message)
        
        self.assertIn("required", str(result))
        self.assertIn("test", str(result))
        self.assertIn("valid=False", str(result))
        self.assertIn("Error message", str(result))


class TestMessage(unittest.TestCase):
    """Tests for the Message class."""
    
    def test_init(self):
        """Test initialization of Message."""
        message = Message(
            text="Error message",
            section_index="1",
            column_index=2,
            record_index=3,
            severity=MessageSeverity.ERROR
        )
        
        self.assertEqual(message.text, "Error message")
        self.assertEqual(message.section_index, "1")
        self.assertEqual(message.column_index, 2)
        self.assertEqual(message.record_index, 3)
        self.assertEqual(message.severity, MessageSeverity.ERROR)
    
    def test_init_defaults(self):
        """Test initialization of Message with default values."""
        message = Message(text="Error message")
        
        self.assertEqual(message.text, "Error message")
        self.assertIsNone(message.section_index)
        self.assertIsNone(message.column_index)
        self.assertIsNone(message.record_index)
        self.assertEqual(message.severity, MessageSeverity.ERROR)
    
    def test_str(self):
        """Test string representation of Message."""
        message = Message(
            text="Error message",
            section_index="1",
            column_index=2,
            record_index=3,
            severity=MessageSeverity.ERROR
        )
        
        self.assertIn("Error message", str(message))
        self.assertIn("section=1", str(message))
        self.assertIn("column=2", str(message))
        self.assertIn("record=3", str(message))
        self.assertIn("ERROR", str(message))


if __name__ == "__main__":
    unittest.main() 