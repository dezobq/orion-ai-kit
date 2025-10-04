// SPDX-License-Identifier: Apache-2.0
module.exports = {
  testEnvironment: 'node',
  reporters: ['default', ['jest-junit', {outputDirectory: 'reports', outputName: 'junit.xml'}]],
  collectCoverage: true,
  coverageReporters: ['cobertura', 'lcov'],
  coverageDirectory: 'reports'
};