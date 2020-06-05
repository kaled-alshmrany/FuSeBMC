struct _IO_FILE;
typedef struct _IO_FILE FILE;
extern struct _IO_FILE *stdin;
extern struct _IO_FILE *stderr;
typedef long unsigned int size_t;
extern void abort (void) __attribute__ ((__nothrow__ , __leaf__)) __attribute__ ((__noreturn__));
extern void exit (int __status) __attribute__ ((__nothrow__ , __leaf__)) __attribute__ ((__noreturn__));
extern char *fgets (char *__restrict __s, int __n, FILE *__restrict __stream);
extern int sscanf (const char *__restrict __s, const char *__restrict __format, ...) __attribute__ ((__nothrow__ , __leaf__));
 extern size_t strlen (const char *__s __attribute__ ((__nothrow__ , __leaf__)) __attribute__ ((__pure__)) __attribute__ ((__nonnull__ (1))));
extern int fprintf (FILE *__restrict __stream, const char *__restrict __format, ...);
 extern void *malloc (size_t __size __attribute__ ((__nothrow__ , __leaf__)) __attribute__ ((__malloc__)));
 extern void *memcpy (void *__restrict __dest, const void *__restrict __src, size_t __n) __attribute__ ((__nothrow__ , __leaf__)) __attribute__ ((__nonnull__ (1, 2)));
 extern char *strcpy (char *__restrict __dest, const char *__restrict __src) __attribute__ ((__nothrow__ , __leaf__)) __attribute__ ((__nonnull__ (1, 2)));
 extern char *strcat (char *__restrict __dest, const char *__restrict __src) __attribute__ ((__nothrow__ , __leaf__)) __attribute__ ((__nonnull__ (1, 2)));
// testcov is tool for validation and execution of test suites.
// This file is part of testcov.
//
// Copyright (C) 2018 - 2020  Dirk Beyer
// All rights reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

#define MAX_INPUT_SIZE 3000
#ifdef GCOV
extern void __gcov_flush(void);
#endif

void abort_prog() {
#ifdef GCOV
  __gcov_flush();
#endif
  abort();
}

void __VERIFIER_assume(int cond) {
  if (!cond) {
    abort_prog();
  }
}

void __VERIFIER_error() {
  fprintf(stderr, "Error found.\n");
  exit(1);
}

char *get_input();

// taken from https://stackoverflow.com/a/32496721
void replace_char(char *str, char find, char replace) {
  char *current_pos = strchr(str, find);
  while (current_pos) {
    *current_pos = replace;
    current_pos = strchr(current_pos, find);
  }
}

void parse_input_from(char *inp_var, char *format, void *destination) {
  char format_with_fallback[13];
  strcpy(format_with_fallback, format);
  strcat(format_with_fallback, "%c%c%c%c");
  if (inp_var[0] == '0' && inp_var[1] == 'x') {
    replace_char(format_with_fallback, 'd', 'x');
  } else {
    if (inp_var[0] == '\'' || inp_var[0] == '\"') {
      int inp_length = strlen(inp_var);
      // Remove ' at the end
      inp_var[inp_length - 1] = '\0';
      // Remove ' in the beginning
      inp_var++;
    }
  }
  char leftover[4];
  int filled = sscanf(inp_var, format_with_fallback, destination, &leftover[0],
                      &leftover[1], &leftover[2], &leftover[3]);
  _Bool is_valid = 1;
  if (filled == 5 || filled == 0) {
    is_valid = 0;
  }
  while (filled > 1) {
    filled--;
    char literal = leftover[filled - 1];
    switch (literal) {
    case 'l':
    case 'L':
    case 'u':
    case 'U':
    case 'f':
    case 'F':
      break;
    default:
      is_valid = 0;
    }
  }

  if (!is_valid) {
    fprintf(stderr, "Can't parse input: '%s'\n", inp_var);
    abort_prog();
  }
}

void parse_input(char *format, void *destination) {
  char *inp_var = get_input();
  parse_input_from(inp_var, format, destination);
}

char __VERIFIER_nondet_char() {
  char val;
  char *inp_var = get_input();
  if (inp_var[0] == '\'') {
    parse_input_from(inp_var, "%c", &val);
  } else {
    parse_input_from(inp_var, "%hhd", &val);
  }
  return val;
}

unsigned char __VERIFIER_nondet_uchar() {
  unsigned char val;
  parse_input("%hhu", &val);
  return val;
}

short __VERIFIER_nondet_short() {
  short val;
  parse_input("%hd", &val);
  return val;
}

unsigned short __VERIFIER_nondet_ushort() {
  unsigned short val;
  parse_input("%hu", &val);
  return val;
}

int __VERIFIER_nondet_int() {
  int val;
  parse_input("%d", &val);
  return val;
}

unsigned int __VERIFIER_nondet_uint() {
  unsigned int val;
  parse_input("%u", &val);
  return val;
}

long __VERIFIER_nondet_long() {
  long val;
  parse_input("%ld", &val);
  return val;
}

unsigned long __VERIFIER_nondet_ulong() {
  unsigned long val;
  parse_input("%lu", &val);
  return val;
}

long long __VERIFIER_nondet_longlong() {
  long long val;
  parse_input("%lld", &val);
  return val;
}

unsigned long long __VERIFIER_nondet_ulonglong() {
  unsigned long long val;
  parse_input("%llu", &val);
  return val;
}

float __VERIFIER_nondet_float() {
  float val;
  parse_input("%f", &val);
  return val;
}

double __VERIFIER_nondet_double() {
  double val;
  parse_input("%lf", &val);
  return val;
}

_Bool __VERIFIER_nondet_bool() { return (_Bool)__VERIFIER_nondet_int(); }

void *__VERIFIER_nondet_pointer() { return (void *)__VERIFIER_nondet_ulong(); }

unsigned int __VERIFIER_nondet_size_t() { return __VERIFIER_nondet_uint(); }

unsigned char __VERIFIER_nondet_u8() { return __VERIFIER_nondet_uchar(); }

unsigned short __VERIFIER_nondet_u16() { return __VERIFIER_nondet_ushort(); }

unsigned int __VERIFIER_nondet_u32() { return __VERIFIER_nondet_uint(); }

unsigned int __VERIFIER_nondet_U32() { return __VERIFIER_nondet_u32(); }

unsigned char __VERIFIER_nondet_unsigned_char() {
  return __VERIFIER_nondet_uchar();
}

unsigned int __VERIFIER_nondet_unsigned() { return __VERIFIER_nondet_uint(); }

const char *__VERIFIER_nondet_string() {
  char *val = malloc(MAX_INPUT_SIZE + 1);
  // Read to end of line
  parse_input("%[^\n]", val);
  return val;
}

char * get_input() {
    char * inp_var = malloc(MAX_INPUT_SIZE);
    char * result = fgets(inp_var, MAX_INPUT_SIZE, stdin);
    if (result == 0) {
        fprintf(stderr, "No more test inputs available, exiting\n");
        exit(1);
    }
    unsigned int input_length = strlen(inp_var)-1;
    /* Remove '\n' at end of input */
    if (inp_var[input_length] == '\n') {
        inp_var[input_length] = '\0';
    }
    return inp_var;
}
