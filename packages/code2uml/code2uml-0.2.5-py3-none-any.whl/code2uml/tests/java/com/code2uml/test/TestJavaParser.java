package com.code2uml.test;

public class TestJavaParser {

    interface ILove {
        void foo();
        void love();
        default int testAdd(int x, int y) { return 0;}
    }

    class Love implements ILove {
        @Override
        public void foo() {
            System.out.println("foo");
        }

        @Override
        public void love() {
            System.out.println("love");
        }
    }

    public void testJavaParser() {
        Love l = new Love();
        l.foo();
        sub();
    }

    public int add(int x, int y) {
        return x + y;
    }

    private int sub() {
        mLove.love();
        return a -b;
    }

    public TestJavaParser() {
        mLove = new Love();
        mLove.foo();
    }

    private int a;
    private int b;
    public int x;
    public static final int GAME = 1;
    private Love mLove;
    private Love mLove2;
}
