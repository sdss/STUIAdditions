import TUI.Base.TestDispatcher

TestDispatcher = TUI.Base.TestDispatcher.TestDispatcher('sop', delay=5)
tuiModel = TestDispatcher.tuiModel
sopTester = TestDispatcher
testData = ('doMangaSequence_ditherSeq="NS", 7',)
sopTester.dispatch(testData)
print('Testing')
