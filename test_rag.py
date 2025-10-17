import json
import requests
import time
from colorama import init, Fore, Style

# Initialize colorama for colored output
init()

# Test configuration
BASE_URL = "http://localhost:5000"
TEST_QUESTIONS = [
    {
        "prompt": "What is Eluvio's main business?",
        "expected_keywords": ["digital content", "distribution", "blockchain-based platform", "premium video","Content Fabric","monetization"],
        "category": "basic"
    },
    {
        "prompt": "What is the Eluvio Content Fabric?",
        "expected_keywords": ["fabric", "blockchain", "content"],
        "category": "technical"
    },
    {
        "prompt": "How does Eluvio use blockchain?",
        "expected_keywords": ["blockchain", "decentralized", "network"],
        "category": "technical"
    },
    {
        "prompt": "What security features does Eluvio provide?",
        "expected_keywords": ["security", "encryption", "DRM"],
        "category": "security"
    },
    {
        "prompt": "When was Eluvio founded?",
        "expected_keywords": ["2017", "founded"],
        "category": "factual"
    },
    {
        "prompt": "What are Eluvio's use cases?",
        "expected_keywords": ["streaming", "NFT", "video"],
        "category": "application"
    },
    {
        "prompt": "Who invented the internet?",  # Out of scope
        "expected_keywords": [],
        "category": "out_of_scope"
    },
    {
        "prompt": "Where is ELuvio at",  # little grammar mistake/ lack of clarity
        "expected_keywords": ["Berkeley", "California"],
        "category": "factual"
    },
    {
        "prompt": "Which industries or partners use Eluvio?", 
        "expected_keywords": ["FOX Corporation","Amazon Studios / MGM","SONY Pictures","Paramount Home Entertainment","Black Eyed Peas"],
        "category": "factual"
    }
    
]


class RAGTester:
    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url
        self.results = []
        
    def print_header(self, text):
        """Print styled header"""
        print("\n" + "=" * 70)
        print(f"{Fore.CYAN}{Style.BRIGHT}{text}{Style.RESET_ALL}")
        print("=" * 70)
    
    def print_success(self, text):
        """Print success message"""
        print(f"{Fore.GREEN}✓ {text}{Style.RESET_ALL}")
    
    def print_error(self, text):
        """Print error message"""
        print(f"{Fore.RED}✗ {text}{Style.RESET_ALL}")
    
    def print_warning(self, text):
        """Print warning message"""
        print(f"{Fore.YELLOW}⚠ {text}{Style.RESET_ALL}")
    
    def print_info(self, text):
        """Print info message"""
        print(f"{Fore.BLUE}ℹ {text}{Style.RESET_ALL}")
    
    def test_health_check(self):
        """Test 1: Health check endpoint"""
        self.print_header("Test 1: Health Check")
        
        try:
            response = requests.get(f"{self.base_url}/health", timeout=5)
            
            if response.status_code == 200:
                self.print_success("Health check passed")
                return True
            else:
                self.print_error(f"Health check failed with status {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            self.print_error("Cannot connect to server. Is it running?")
            self.print_info("Start server with: python server.py")
            return False
        except Exception as e:
            self.print_error(f"Health check error: {e}")
            return False
    
    def test_ask_endpoint(self, question_data):
        """Test a single question"""
        prompt = question_data["prompt"]
        expected_keywords = question_data["expected_keywords"]
        category = question_data["category"]
        
        print(f"\n{Fore.YELLOW}Question ({category}):{Style.RESET_ALL} {prompt}")
        
        try:
            start_time = time.time()
            
            response = requests.post(
                f"{self.base_url}/ask",
                json={"prompt": prompt},
                timeout=50             # timeout set to 50s
            )
            
            elapsed_time = time.time() - start_time
            
            if response.status_code != 200:
                self.print_error(f"Request failed with status {response.status_code}")
                return {
                    "question": prompt,
                    "status": "failed",
                    "error": f"Status {response.status_code}"
                }
            
            data = response.json()
            answer = data.get("response", "")
            
            print(f"{Fore.GREEN}Answer:{Style.RESET_ALL} {answer[:200]}{'...' if len(answer) > 200 else ''}")
            print(f"{Fore.CYAN}Time:{Style.RESET_ALL} {elapsed_time:.2f}s")
            
            # Check for keywords
            if expected_keywords:
                found_keywords = [kw for kw in expected_keywords 
                                 if kw.lower() in answer.lower()]
                
                if len(found_keywords) >= len(expected_keywords) * 0.5:  # at least 50%
                    self.print_success(f"Found keywords: {', '.join(found_keywords)}")
                    quality = "good"
                else:
                    self.print_warning(f"Missing keywords. Found: {found_keywords}")
                    quality = "partial"
            else:
                # Out of scope questions 
                if any(phrase in answer.lower() for phrase in 
                       ["don't have", "not enough information", "cannot answer"]):
                    self.print_success("Correctly handled out-of-scope question")
                    quality = "good"
                else:
                    self.print_warning("May have hallucinated for out-of-scope question")
                    quality = "warning"
            
            return {
                "question": prompt,
                "answer": answer,
                "quality": quality,
                "time": elapsed_time,
            }
            
        except requests.exceptions.Timeout:
            self.print_error("Request timed out (>30s)")
            return {
                "question": prompt,
                "status": "timeout",
                "error": "Timeout"
            }
        except Exception as e:
            self.print_error(f"Error: {e}")
            return {
                "question": prompt,
                "status": "error",
                "error": str(e)
            }
    
    def test_all_questions(self):
        """Test 2: All predefined questions"""
        self.print_header("Test 2: Question Answering Quality")
        
        for i, question_data in enumerate(TEST_QUESTIONS, 1):
            print(f"\n{Fore.MAGENTA}[{i}/{len(TEST_QUESTIONS)}]{Style.RESET_ALL}")
            result = self.test_ask_endpoint(question_data)
            self.results.append(result)
            time.sleep(0.5)  
    
    def test_edge_cases(self):
        """Test 3: Edge cases"""
        self.print_header("Test 3: Edge Cases")
        
        edge_cases = [
            {
                "name": "Empty prompt",
                "data": {"prompt": ""},
                "expect_error": True
            },
            {
                "name": "Very long prompt",
                "data": {"prompt": "What " + "is " * 100 + "Eluvio?"},
                "expect_error": False
            },
            {
                "name": "Very short prompt",
                "data": {"prompt": "Eluvio"},
                "expect_error": False
            },
            {
                "name": "typo question",
                "data": {"prompt": "whta is EVIE"},
                "expect_error": False
            },
            {
                "name": "Special characters",
                "data": {"prompt": "What's #$@@Eluvio's CEO's name@#$%^?"},
                "expect_error": False
            },
            {
                "name": "Essay like prompt",
                "data": {"prompt": "I am conducting a research project about decentralized media delivery systems and I would like to know everything possible about Eluvio’s design, architecture, blockchain components, security layers, partnerships, awards, and overall impact on the video streaming ecosystem worldwide. Please include examples and detailed explanation."},
                "expect_error": False
            },
            {
                "name": "Missing prompt field",
                "data": {"question": "What does Eluvio do?"},
                "expect_error": True
            }
        ]
        
        for case in edge_cases:
            print(f"\n{Fore.YELLOW}Testing:{Style.RESET_ALL} {case['name']}")
            
            try:
                response = requests.post(
                    f"{self.base_url}/ask",
                    json=case["data"],
                    timeout=30            # this timeout set to be 30s
                )
                
                # Print response content
                try:
                    resp_json = response.json()
                    print(f"{Fore.CYAN}Server response:{Style.RESET_ALL} {json.dumps(resp_json, indent=2)}")
                except Exception:
                    print(f"{Fore.CYAN}Raw response text:{Style.RESET_ALL} {response.text[:300]}")
                
                
                if case["expect_error"]:
                    if response.status_code != 200:
                        self.print_success(f"Correctly rejected invalid input (status {response.status_code})")
                    else:
                        self.print_warning("Should have rejected invalid input")
                else:
                    if response.status_code == 200:
                        self.print_success("Handled edge case successfully")
                    else:
                        self.print_error(f"Failed to handle edge case (status {response.status_code})")
                        
            except Exception as e:
                self.print_error(f"Error: {e}")
    
    #def test_question_in_different_format():
    
    def generate_performance(self):
        """Generate test performance"""
        self.print_header("Test Performance")

        times = [r["time"] for r in self.results if "time" in r]
        if times:
            avg_time = sum(times) / len(times)
            print(f"\n{Fore.CYAN}Performance:{Style.RESET_ALL}")
            print(f"  Average response time: {avg_time:.2f}s")
            print(f"  Fastest: {min(times):.2f}s")
            print(f"  Slowest: {max(times):.2f}s")
        
    
    def save_results(self, filename="test_results.json"):
        """Save test results to file"""
        with open(filename, 'w') as f:
            json.dump({
                "test_time": time.strftime("%Y-%m-%d %H:%M:%S"),
                "total_tests": len(self.results),
                "results": self.results
            }, f, indent=2)
        
        self.print_success(f"Results saved to {filename}")
    
    def run_all_tests(self):
        """Run complete test suite"""
        print(f"\n{Fore.MAGENTA}{Style.BRIGHT}")
        self.print_header("Eluvio RAG System - Test")
        print(Style.RESET_ALL)
        
        # Test 1: Health check
        if not self.test_health_check():
            self.print_error("\nServer is not running. Aborting tests.")
            return False
        
        # Test 2: Question answering
        self.test_all_questions()
        
        # Test 3: Edge cases
        self.test_edge_cases()
        
        # summary
        self.generate_performance()
        
        self.save_results()
        
        print(f"\n{Fore.GREEN}{Style.BRIGHT}✓ Test suite completed!{Style.RESET_ALL}\n")
        return True


def main():
    """Main test runner"""
    tester = RAGTester()
    tester.run_all_tests()


if __name__ == "__main__":
    main()